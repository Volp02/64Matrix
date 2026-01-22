import logging
import sys

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
        self._canvas = self.matrix.CreateFrameCanvas()
        
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

    def clear(self):
        """Clears the current canvas."""
        self._canvas.Clear()

    def fill(self, r, g, b):
        """Fills the entire canvas with a solid color."""
        self._canvas.Fill(r, g, b)

    def set_pixel(self, x, y, r, g, b):
        """Sets a single pixel on the canvas."""
        self._canvas.SetPixel(x, y, r, g, b)

    def draw_text(self, font, x, y, color, text):
        """Helper to draw text using the graphics module."""
        # Note: graphics.DrawText draws directly to the canvas
        return graphics.DrawText(self._canvas, font, x, y, color, text)

    def swap_canvas(self):
        """Updates the display with the current canvas and returns a new one."""
        self._canvas = self.matrix.SwapOnVSync(self._canvas)
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
