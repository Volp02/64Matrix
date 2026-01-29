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
        self.options.gpio_slowdown = 4  # Aggressive slowdown to fix flickering
        self.options.pwm_lsb_nanoseconds = 130 # Reduces low-brightness ghosting
        self.options.scan_mode = 0 # Standard progressive scan
        
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
            # NOTE: We only intercept SetImage now. Others delegate to real canvas.
            if name in ('_real_canvas', '_matrix_driver', 'SetImage'):
                return object.__getattribute__(self, name)
            
            # For all other attributes, delegate to real canvas
            real_canvas = object.__getattribute__(self, '_real_canvas')
            return getattr(real_canvas, name)
        
        def SetImage(self, img, *args, **kwargs):
            """Intercept SetImage to update shadow buffer."""
            real_canvas = object.__getattribute__(self, '_real_canvas')
            matrix_driver = object.__getattribute__(self, '_matrix_driver')
            result = real_canvas.SetImage(img, *args, **kwargs)
            # Only update shadow buffer if we are actually tracking it (optimization)
            # For now, we update it because SetImage is usually once per frame
            matrix_driver.update_shadow_from_image(img)
            return result
        
        # NOTE: We do NOT intercept SetPixel, Fill, or Clear anymore.
        # The overhead of a Python function call + lock + PIL update PER PIXEL is too high (kills FPS).
        # Scenes using SetPixel will rely on valid canvas readback or might not show in preview perfectly.


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
             # The rgbmatrix library simply takes a value, usually 0-100. 
             # Some older versions might take 0-255? Standard hzeller/rpi-rgb-led-matrix usually uses 0-100.
             # We will pass the 0-100 value directly.
            if hasattr(self.matrix, 'brightness'):
                self.matrix.brightness = self._brightness
                logger.info(f"Hardware brightness set to {self._brightness}%")
            elif hasattr(self.matrix, 'SetBrightness'):
                # Pass the raw 0-100 value. 
                # If the user sees it's too dim, we might have issues with 0-255 scaling,
                # but 'brightness' property usually handles this.
                self.matrix.SetBrightness(int(self._brightness))
                logger.info(f"Hardware brightness set to {self._brightness}% (SetBrightness)")
            else:
                # Software dimming fallback
                logger.debug(f"Hardware brightness not supported, using software dimming: {self._brightness}%")
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
        Capture the current canvas as a PIL Image.
        Returns a PIL Image object (64x64 RGB) or None if capture fails.
        """
        try:
            # First, check if the shadow buffer is actively being updated (e.g. by SetImage)
            # We can't know for sure, but we can assume if it's not black, it's valid.
            # However, with SetPixel changes, the shadow buffer might stay black or stale.
            
            # NOTE: For performance, we prioritize the shadow buffer if it has content.
            # But since we removed SetPixel interception, we MUST fallback to reading the canvas
            # if we suspect the shadow buffer is not representing the current state.
            
            use_shadow = False
            with self._shadow_lock:
                # Simple heuristic: if shadow buffer has non-black content, use it?
                # Actually, worst case: we show a stale image. Best case: it's fast.
                # Given the user reported LOW FPS, we want to avoid reading hardware canvas if possible.
                # But if they use a script with SetPixel, shadow buffer will be EMPTY.
                if self._shadow_buffer.getbbox(): # Returns None if image is all black
                    use_shadow = True
                    img = self._shadow_buffer.copy()

            if use_shadow:
                return img

            # If shadow buffer is empty, it means we are likely using SetPixel directly.
            # We MUST read from the hardware canvas.
            
            # Method 1: Try built-in ToImage() if available (some bindings have this)
            if hasattr(self._raw_canvas, 'ToImage'):
                 return self._raw_canvas.ToImage()

            # Method 2: Try GetPixel loop (Slow, but necessary fallback)
            # We optimize this by not creating a new image every time if possible, but here we just do it.
            if hasattr(self._raw_canvas, 'GetPixel'):
                img = Image.new('RGB', (self.width, self.height))
                pixels = []
                # optimization: local lookup
                get_pixel = self._raw_canvas.GetPixel
                width, height = self.width, self.height
                
                for y in range(height):
                    for x in range(width):
                        try:
                            # Note: rgbmatrix might return (r,g,b) or integer
                            p = get_pixel(x, y)
                            pixels.append(p)
                        except:
                            pixels.append((0,0,0))
                img.putdata(pixels)
                return img
                
            return None
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
