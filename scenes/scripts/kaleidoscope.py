from app.core.base_scene import BaseScene
import math
import random


class Kaleidoscope(BaseScene):
    """
    Mesmerizing kaleidoscope with symmetric, mirrored patterns.
    Features 6-fold or 8-fold symmetry with rotating geometric shapes.
    """
    
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        
        # Center of the kaleidoscope
        self.center_x = self.width / 2
        self.center_y = self.height / 2
        
        # Animation parameters
        self.time = 0.0
        self.rotation = 0.0
        self.rotation_speed = 0.3  # Radians per second
        
        # Symmetry (6 or 8 fold)
        self.symmetry = 6
        
        # Color palette - vibrant colors
        self.base_colors = [
            (255, 50, 100),   # Pink-red
            (255, 150, 50),   # Orange
            (255, 255, 50),   # Yellow
            (50, 255, 100),   # Green
            (50, 200, 255),   # Cyan
            (100, 100, 255),  # Blue
            (200, 50, 255),   # Purple
            (255, 100, 200),  # Magenta
        ]
        
        # Pattern elements - shapes that make up the kaleidoscope
        self.shapes = self._generate_shapes()
        
        # Color shift phase
        self.color_phase = 0.0
        
    def _generate_shapes(self):
        """Generate random geometric shapes for the pattern"""
        shapes = []
        
        # Create several shapes at random positions in the "wedge"
        for _ in range(12):
            # Position in polar coordinates (within one wedge)
            r = random.uniform(5, 30)  # Distance from center
            theta = random.uniform(0, math.pi / self.symmetry)  # Angle within wedge
            
            shape = {
                'r': r,
                'theta': theta,
                'type': random.choice(['circle', 'triangle', 'diamond', 'line']),
                'size': random.uniform(2, 6),
                'color_idx': random.randint(0, len(self.base_colors) - 1),
                'pulse_speed': random.uniform(1, 3),
                'pulse_phase': random.uniform(0, math.pi * 2),
                'orbit_speed': random.uniform(-0.5, 0.5),  # Shapes slowly orbit
            }
            shapes.append(shape)
        
        return shapes
    
    def _get_color(self, color_idx, brightness=1.0):
        """Get a color with phase shift for smooth transitions"""
        # Shift color index over time for color cycling
        shifted_idx = (color_idx + self.color_phase) % len(self.base_colors)
        
        # Interpolate between two colors for smooth transition
        idx1 = int(shifted_idx) % len(self.base_colors)
        idx2 = (idx1 + 1) % len(self.base_colors)
        t = shifted_idx - int(shifted_idx)
        
        c1 = self.base_colors[idx1]
        c2 = self.base_colors[idx2]
        
        r = int((c1[0] * (1 - t) + c2[0] * t) * brightness)
        g = int((c1[1] * (1 - t) + c2[1] * t) * brightness)
        b = int((c1[2] * (1 - t) + c2[2] * t) * brightness)
        
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
    
    def _draw_shape_at(self, canvas, x, y, shape_type, size, color):
        """Draw a shape centered at (x, y)"""
        r, g, b = color
        ix, iy = int(x), int(y)
        
        if shape_type == 'circle':
            # Filled circle
            radius = int(size)
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx*dx + dy*dy <= radius*radius:
                        px, py = ix + dx, iy + dy
                        if 0 <= px < self.width and 0 <= py < self.height:
                            canvas.SetPixel(px, py, r, g, b)
        
        elif shape_type == 'triangle':
            # Simple triangle pointing outward
            half = int(size)
            for dy in range(-half, half + 1):
                width = int((half - abs(dy)) * 0.8)
                for dx in range(-width, width + 1):
                    px, py = ix + dx, iy + dy
                    if 0 <= px < self.width and 0 <= py < self.height:
                        canvas.SetPixel(px, py, r, g, b)
        
        elif shape_type == 'diamond':
            # Diamond shape
            half = int(size)
            for dy in range(-half, half + 1):
                width = half - abs(dy)
                for dx in range(-width, width + 1):
                    px, py = ix + dx, iy + dy
                    if 0 <= px < self.width and 0 <= py < self.height:
                        canvas.SetPixel(px, py, r, g, b)
        
        elif shape_type == 'line':
            # Radial line
            length = int(size * 2)
            for i in range(length):
                px = ix + i
                if 0 <= px < self.width and 0 <= iy < self.height:
                    canvas.SetPixel(px, iy, r, g, b)
    
    def _polar_to_cartesian(self, r, theta):
        """Convert polar coordinates to cartesian, centered on display"""
        x = self.center_x + r * math.cos(theta)
        y = self.center_y + r * math.sin(theta)
        return x, y
    
    def update(self, dt):
        self.time += dt
        
        # Rotate the entire pattern
        self.rotation += self.rotation_speed * dt
        
        # Cycle colors slowly
        self.color_phase += dt * 0.2
        
        # Update shape positions (they orbit slowly)
        for shape in self.shapes:
            shape['theta'] += shape['orbit_speed'] * dt
            shape['pulse_phase'] += shape['pulse_speed'] * dt
            
            # Keep theta within the wedge
            wedge_size = math.pi / self.symmetry
            if shape['theta'] < 0:
                shape['theta'] += wedge_size
            elif shape['theta'] > wedge_size:
                shape['theta'] -= wedge_size
        
        # Occasionally regenerate shapes for variety
        if random.random() < 0.002:  # Very rarely
            idx = random.randint(0, len(self.shapes) - 1)
            self.shapes[idx] = {
                'r': random.uniform(5, 30),
                'theta': random.uniform(0, math.pi / self.symmetry),
                'type': random.choice(['circle', 'triangle', 'diamond', 'line']),
                'size': random.uniform(2, 6),
                'color_idx': random.randint(0, len(self.base_colors) - 1),
                'pulse_speed': random.uniform(1, 3),
                'pulse_phase': random.uniform(0, math.pi * 2),
                'orbit_speed': random.uniform(-0.5, 0.5),
            }
    
    def draw(self, canvas):
        # Dark background
        canvas.Fill(5, 5, 15)
        
        # Draw radial gradient background for depth
        for y in range(self.height):
            for x in range(self.width):
                dx = x - self.center_x
                dy = y - self.center_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                # Subtle radial pattern in background
                angle = math.atan2(dy, dx) + self.rotation * 0.5
                pattern = math.sin(angle * self.symmetry + self.time) * 0.5 + 0.5
                pattern *= math.sin(dist * 0.15 - self.time * 0.5) * 0.5 + 0.5
                
                # Very subtle background color
                bg_r = int(10 + pattern * 15)
                bg_g = int(5 + pattern * 10)
                bg_b = int(20 + pattern * 20)
                
                canvas.SetPixel(x, y, bg_r, bg_g, bg_b)
        
        # Draw each shape with full symmetry
        for shape in self.shapes:
            # Pulsing size
            pulse = math.sin(shape['pulse_phase']) * 0.3 + 1.0
            size = shape['size'] * pulse
            
            # Pulsing brightness
            brightness = 0.7 + math.sin(shape['pulse_phase'] * 0.7) * 0.3
            
            color = self._get_color(shape['color_idx'], brightness)
            
            # Draw in all symmetric positions
            for i in range(self.symmetry):
                # Angle for this segment
                segment_angle = (2 * math.pi / self.symmetry) * i
                
                # Normal position
                theta1 = shape['theta'] + segment_angle + self.rotation
                x1, y1 = self._polar_to_cartesian(shape['r'], theta1)
                self._draw_shape_at(canvas, x1, y1, shape['type'], size, color)
                
                # Mirrored position (flip within segment)
                theta2 = -shape['theta'] + segment_angle + self.rotation
                x2, y2 = self._polar_to_cartesian(shape['r'], theta2)
                self._draw_shape_at(canvas, x2, y2, shape['type'], size, color)
        
        # Draw center glow
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 4:
                    brightness = 1.0 - dist / 4
                    # Cycling center color
                    center_color = self._get_color(int(self.time * 2) % len(self.base_colors), brightness)
                    px = int(self.center_x + dx)
                    py = int(self.center_y + dy)
                    if 0 <= px < self.width and 0 <= py < self.height:
                        canvas.SetPixel(px, py, center_color[0], center_color[1], center_color[2])
