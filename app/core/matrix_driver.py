import logging
import sys
import threading
from PIL import Image

# Configure logging
logger = logging.getLogger(__name__)

# Try to import the real hardware library
try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
    from rgbmatrix import graphics
    EMULATED = False
    logger.info("Loaded real rgbmatrix hardware driver.")
except ImportError:
    # Fallback to the emulator
    try:
        from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
        EMULATED = True
        logger.warning("rgbmatrix not found. Loaded RGBMatrixEmulator.")
    except ImportError:
        logger.error("Neither rgbmatrix nor RGBMatrixEmulator found. Exiting.")
        sys.exit(1)

class MatrixDriver:
    def __init__(self, width=64, height=64, chain=1, parallel=1, brightness=100):
        self.options = RGBMatrixOptions()
        self.options.rows = height
        self.options.cols = width
        self.options.chain_length = chain
        self.options.parallel = parallel
        self.options.hardware_mapping = 'adafruit-hat'  # Default for RPi
        
        # Brightness: RGBMatrix uses 0-100, but some implementations use 0-255
        # We'll store as 0-100 and convert if needed
        self._brightness = brightness
        self.options.brightness = brightness
        
        # If emulated, we might want to relax some hardware specific settings or keep them as is
        # The emulator usually ignores hardware specific options safely
        
        self.matrix = RGBMatrix(options=self.options)
        self._raw_canvas = self.matrix.CreateFrameCanvas()
        
        # Shadow buffer for preview capture
        # We maintain a parallel PIL Image that mirrors what's drawn on the canvas
        self._shadow_buffer = Image.new('RGB', (self.width, self.height), color='black')
        self._shadow_lock = threading.Lock()
        
        # Wrap canvas to intercept SetImage calls
        self._canvas = self._CanvasWrapper(self._raw_canvas, self)
        
    @property
    def width(self):
        return self.matrix.width
    
    @property
    def height(self):
        return self.matrix.height
        
    @property
    def canvas(self):
        """Exposes the current canvas for drawing."""
        return self._canvas
    
    class _CanvasWrapper:
        """Wrapper around the real canvas that intercepts drawing calls to update shadow buffer."""
        def __init__(self, real_canvas, matrix_driver):
            object.__setattr__(self, '_real_canvas', real_canvas)
            object.__setattr__(self, '_matrix_driver', matrix_driver)
        
        def __getattribute__(self, name):
            # Handle our own attributes and intercepted methods
            if name in ('_real_canvas', '_matrix_driver', 'SetImage', 'SetPixel', 'Fill', 'Clear'):
                return object.__getattribute__(self, name)
            
            # For all other attributes, delegate to real canvas
            real_canvas = object.__getattribute__(self, '_real_canvas')
            return getattr(real_canvas, name)
        
        def SetImage(self, img, *args, **kwargs):
            """Intercept SetImage to update shadow buffer."""
            real_canvas = object.__getattribute__(self, '_real_canvas')
            matrix_driver = object.__getattribute__(self, '_matrix_driver')
            result = real_canvas.SetImage(img, *args, **kwargs)
            matrix_driver.update_shadow_from_image(img)
            return result
        
        def SetPixel(self, x, y, r, g, b):
            """Intercept SetPixel to update shadow buffer."""
            real_canvas = object.__getattribute__(self, '_real_canvas')
            matrix_driver = object.__getattribute__(self, '_matrix_driver')
            result = real_canvas.SetPixel(x, y, r, g, b)
            with matrix_driver._shadow_lock:
                if 0 <= x < matrix_driver.width and 0 <= y < matrix_driver.height:
                    matrix_driver._shadow_buffer.putpixel((x, y), (r, g, b))
            return result
        
        def Fill(self, r, g, b):
            """Intercept Fill to update shadow buffer."""
            real_canvas = object.__getattribute__(self, '_real_canvas')
            matrix_driver = object.__getattribute__(self, '_matrix_driver')
            result = real_canvas.Fill(r, g, b)
            with matrix_driver._shadow_lock:
                matrix_driver._shadow_buffer = Image.new('RGB', 
                    (matrix_driver.width, matrix_driver.height), color=(r, g, b))
            return result
        
        def Clear(self):
            """Intercept Clear to update shadow buffer."""
            real_canvas = object.__getattribute__(self, '_real_canvas')
            matrix_driver = object.__getattribute__(self, '_matrix_driver')
            result = real_canvas.Clear()
            with matrix_driver._shadow_lock:
                matrix_driver._shadow_buffer = Image.new('RGB', 
                    (matrix_driver.width, matrix_driver.height), color='black')
            return result

    def clear(self):
        """Clears the current canvas."""
        self._canvas.Clear()  # Wrapper handles shadow buffer update

    def fill(self, r, g, b):
        """Fills the entire canvas with a solid color."""
        self._canvas.Fill(r, g, b)  # Wrapper handles shadow buffer update

    def set_pixel(self, x, y, r, g, b):
        """Sets a single pixel on the canvas."""
        self._canvas.SetPixel(x, y, r, g, b)  # Wrapper handles shadow buffer update

    def draw_text(self, font, x, y, color, text):
        """Helper to draw text using the graphics module."""
        # Note: graphics.DrawText draws directly to the canvas
        return graphics.DrawText(self._canvas, font, x, y, color, text)

    def swap_canvas(self):
        """Updates the display with the current canvas and returns a new one."""
        # Swap the underlying raw canvas
        self._raw_canvas = self.matrix.SwapOnVSync(self._raw_canvas)
        # Re-wrap the new canvas
        self._canvas = self._CanvasWrapper(self._raw_canvas, self)
        return self._canvas
    
    def set_brightness(self, brightness):
        """
        Set the brightness of the matrix (0-100).
        Note: Some RGBMatrix implementations require restart to apply brightness changes.
        For dynamic brightness, we apply software dimming by scaling pixel values.
        """
        self._brightness = max(0, min(100, brightness))
        
        # Try to set hardware brightness if supported
        try:
            if hasattr(self.matrix, 'SetBrightness'):
                # Convert 0-100 to 0-255 if needed, or use directly
                brightness_value = int(self._brightness * 2.55) if brightness <= 100 else int(self._brightness)
                self.matrix.SetBrightness(brightness_value)
                logger.info(f"Hardware brightness set to {brightness}%")
            else:
                # Software dimming: store brightness multiplier for pixel operations
                logger.debug(f"Hardware brightness not supported, using software dimming: {brightness}%")
        except Exception as e:
            logger.warning(f"Failed to set hardware brightness: {e}. Using software dimming.")
    
    def get_brightness(self):
        """Get current brightness (0-100)."""
        return self._brightness
    
    def apply_brightness_to_pixel(self, r, g, b):
        """
        Apply brightness multiplier to RGB values for software dimming.
        Returns scaled RGB tuple.
        """
        multiplier = self._brightness / 100.0
        return (
            int(r * multiplier),
            int(g * multiplier),
            int(b * multiplier)
        )
    
    def capture_frame(self):
        """
        Capture the current canvas as a PIL Image using the shadow buffer.
        Falls back to reading pixels from canvas if shadow buffer is empty/black.
        Returns a PIL Image object (64x64 RGB) or None if capture fails.
        """
        try:
            # Use shadow buffer - it's always up to date since we update it on every draw call
            with self._shadow_lock:
                img = self._shadow_buffer.copy()
            
            # Fallback: If shadow buffer appears to be all black, try reading from canvas
            # Check if image is all black (might mean shadow buffer wasn't updated)
            pixels = list(img.getdata())
            if all(p == (0, 0, 0) for p in pixels):
                # Try multiple fallback methods
                fallback_img = None
                
                # Method 1: Try GetPixel if available
                try:
                    if hasattr(self._raw_canvas, 'GetPixel'):
                        fallback_img = Image.new('RGB', (self.width, self.height))
                        fallback_pixels = []
                        for y in range(self.height):
                            for x in range(self.width):
                                try:
                                    r, g, b = self._raw_canvas.GetPixel(x, y)
                                    fallback_pixels.append((r, g, b))
                                except:
                                    fallback_pixels.append((0, 0, 0))
                        fallback_img.putdata(fallback_pixels)
                except Exception as e:
                    logger.debug(f"GetPixel fallback failed: {e}")
                
                # Method 2: For emulator, try accessing pygame surface
                if not fallback_img and EMULATED:
                    try:
                        # RGBMatrixEmulator might expose the display adapter's surface
                        if hasattr(self.matrix, 'display_adapter') and hasattr(self.matrix.display_adapter, 'surface'):
                            import pygame
                            surface = self.matrix.display_adapter.surface
                            if surface:
                                img_str = pygame.image.tostring(surface, 'RGB')
                                fallback_img = Image.frombytes('RGB', (self.width, self.height), img_str)
                    except Exception as e:
                        logger.debug(f"Pygame surface fallback failed: {e}")
                
                if fallback_img:
                    # Update shadow buffer with what we read
                    with self._shadow_lock:
                        self._shadow_buffer = fallback_img.copy()
                    return fallback_img
            
            return img
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def update_shadow_from_image(self, img):
        """
        Update the shadow buffer from a PIL Image (used by SetImage calls).
        This is called when scenes use SetImage directly on the canvas.
        """
        try:
            if img and hasattr(img, 'size'):
                with self._shadow_lock:
                    # Resize if needed and convert to RGB
                    if img.size != (self.width, self.height):
                        img = img.resize((self.width, self.height), Image.Resampling.NEAREST)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    self._shadow_buffer = img.copy()
        except Exception as e:
            logger.debug(f"Failed to update shadow buffer from image: {e}")
