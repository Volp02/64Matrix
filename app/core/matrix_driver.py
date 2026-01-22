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
    def __init__(self, width=64, height=64, chain=1, parallel=1):
        self.options = RGBMatrixOptions()
        self.options.rows = height
        self.options.cols = width
        self.options.chain_length = chain
        self.options.parallel = parallel
        self.options.hardware_mapping = 'adafruit-hat'  # Default for RPi
        
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
