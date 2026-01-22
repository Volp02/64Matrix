from app.core.base_scene import BaseScene
import math


class MandelbrotZoom(BaseScene):
    """
    Mesmerizing Mandelbrot fractal with continuous zoom.
    Reveals infinite detail as it zooms deeper into the fractal.
    """
    
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        
        # Center point to zoom into (interesting point in Mandelbrot set)
        # This is a famous point with interesting detail
        self.center_real = -0.77568377
        self.center_imag = 0.13646737
        
        # Starting zoom level
        self.zoom = 1.0
        
        # Zoom speed (exponential zoom)
        self.zoom_speed = 1.15  # Multiply zoom by this per second
        
        # Animation time
        self.time = 0.0
        
        # Color cycling phase
        self.color_phase = 0.0
        
        # Max iterations for Mandelbrot calculation
        self.max_iterations = 80
        
        # Color palette - rainbow colors
        self.colors = self._generate_rainbow_palette(256)
        
    def _generate_rainbow_palette(self, num_colors):
        """Generate a rainbow color palette"""
        palette = []
        for i in range(num_colors):
            # Create smooth rainbow gradient
            hue = (i / num_colors) * 6.0  # 0 to 6 (full rainbow cycle)
            
            # Convert HSV to RGB
            sector = int(hue)
            frac = hue - sector
            
            if sector == 0:
                r, g, b = 255, int(255 * frac), 0
            elif sector == 1:
                r, g, b = int(255 * (1 - frac)), 255, 0
            elif sector == 2:
                r, g, b = 0, 255, int(255 * frac)
            elif sector == 3:
                r, g, b = 0, int(255 * (1 - frac)), 255
            elif sector == 4:
                r, g, b = int(255 * frac), 0, 255
            else:  # sector == 5
                r, g, b = 255, 0, int(255 * (1 - frac))
            
            palette.append((r, g, b))
        
        return palette
    
    def _mandelbrot_iterations(self, real, imag):
        """
        Calculate Mandelbrot iterations for a point.
        Returns number of iterations before escape, or max_iterations if in set.
        """
        z_real = 0.0
        z_imag = 0.0
        
        for i in range(self.max_iterations):
            # z = z^2 + c
            z_real_sq = z_real * z_real
            z_imag_sq = z_imag * z_imag
            
            # Check if escaped (|z| > 2)
            if z_real_sq + z_imag_sq > 4.0:
                return i
            
            # Calculate new z
            z_imag = 2.0 * z_real * z_imag + imag
            z_real = z_real_sq - z_imag_sq + real
        
        return self.max_iterations
    
    def _get_color(self, iterations):
        """Get color for iteration count with color cycling"""
        if iterations >= self.max_iterations:
            # Inside the set - black
            return (0, 0, 0)
        
        # Map iterations to color with phase shift for animation
        color_idx = int((iterations + self.color_phase * 50) % len(self.colors))
        return self.colors[color_idx]
    
    def update(self, dt):
        self.time += dt
        
        # Exponential zoom
        self.zoom *= math.pow(self.zoom_speed, dt)
        
        # Cycle colors slowly
        self.color_phase += dt * 0.3
        
        # Reset zoom if it gets too extreme (to avoid precision issues)
        if self.zoom > 1e10:
            self.zoom = 1.0
            self.time = 0.0
    
    def draw(self, canvas):
        # Dark background
        canvas.Fill(0, 0, 0)
        
        # Calculate viewport bounds based on zoom
        # At zoom=1, we see roughly -2 to 2 in both axes
        view_size = 4.0 / self.zoom
        
        # Center the view on our zoom point
        min_real = self.center_real - view_size / 2
        max_real = self.center_real + view_size / 2
        min_imag = self.center_imag - view_size / 2
        max_imag = self.center_imag + view_size / 2
        
        # Calculate step size per pixel
        real_step = (max_real - min_real) / self.width
        imag_step = (max_imag - min_imag) / self.height
        
        # Draw Mandelbrot set
        for y in range(self.height):
            imag = min_imag + y * imag_step
            for x in range(self.width):
                real = min_real + x * real_step
                
                # Calculate Mandelbrot iterations
                iterations = self._mandelbrot_iterations(real, imag)
                
                # Get color
                r, g, b = self._get_color(iterations)
                
                canvas.SetPixel(x, y, r, g, b)
