from app.core.base_scene import BaseScene
import math
import random

class DoublePendulum(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        
        # Physics Constants
        self.r1 = 15.0  # Length of rod 1
        self.r2 = 12.0  # Length of rod 2
        self.m1 = 10.0  # Mass 1
        self.m2 = 10.0  # Mass 2
        self.g = 1.0    # Gravity (tuned for speed)
        
        # State
        self.a1 = math.pi / 2  # Angle 1
        self.a2 = math.pi / 2  # Angle 2
        self.a1_v = 0.0        # Angular velocity 1
        self.a2_v = 0.0        # Angular velocity 2
        
        # Trail
        self.trail = []
        self.max_trail = 100
        
        # Origin (Center of screen)
        self.cx = self.width / 2
        self.cy = self.height / 3

    def update(self, dt):
        # Double Pendulum Physics (Lagrangian Mechanics)
        # Using simple Euler integration, might need small steps or RK4 for stability
        # But for visual effect, this standard formula is usually fine if clamped
        
        # Scale dt to simulation speed
        dt *= 5.0 # Speed up simulation
        
        # Aliases for readability
        r1, r2 = self.r1, self.r2
        m1, m2 = self.m1, self.m2
        a1, a2 = self.a1, self.a2
        a1_v, a2_v = self.a1_v, self.a2_v
        g = self.g
        
        # Calculate accelerations
        num1 = -g * (2 * m1 + m2) * math.sin(a1)
        num2 = -m2 * g * math.sin(a1 - 2 * a2)
        num3 = -2 * math.sin(a1 - a2) * m2
        num4 = a2_v * a2_v * r2 + a1_v * a1_v * r1 * math.cos(a1 - a2)
        den = r1 * (2 * m1 + m2 - m2 * math.cos(2 * a1 - 2 * a2))
        a1_a = (num1 + num2 + num3 * num4) / den

        num1 = 2 * math.sin(a1 - a2)
        num2 = (a1_v * a1_v * r1 * (m1 + m2))
        num3 = g * (m1 + m2) * math.cos(a1)
        num4 = a2_v * a2_v * r2 * m2 * math.cos(a1 - a2)
        den = r2 * (2 * m1 + m2 - m2 * math.cos(2 * a1 - 2 * a2))
        a2_a = (num1 * (num2 + num3 + num4)) / den

        # Update Velocity
        self.a1_v += a1_a * dt
        self.a2_v += a2_a * dt
        
        # Damping (Friction) to prevent exploding energy over time
        self.a1_v *= 0.999
        self.a2_v *= 0.999
        
        # Update Position
        self.a1 += self.a1_v * dt
        self.a2 += self.a2_v * dt
        
        # Calculate positions for drawing
        x1 = self.r1 * math.sin(self.a1) + self.cx
        y1 = self.r1 * math.cos(self.a1) + self.cy
        
        x2 = x1 + self.r2 * math.sin(self.a2)
        y2 = y1 + self.r2 * math.cos(self.a2)
        
        # Add to trail
        self.trail.append((x2, y2))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

    def draw(self, canvas):
        # Calculate current positions
        x1 = self.r1 * math.sin(self.a1) + self.cx
        y1 = self.r1 * math.cos(self.a1) + self.cy
        
        x2 = x1 + self.r2 * math.sin(self.a2)
        y2 = y1 + self.r2 * math.cos(self.a2)
        
        # Draw Trail
        for i, (tx, ty) in enumerate(self.trail):
            # Fade intensity based on index
            alpha = i / len(self.trail)
            r, g, b = int(0 * alpha), int(255 * alpha), int(255 * alpha)
            
            if 0 <= tx < self.width and 0 <= ty < self.height:
                canvas.SetPixel(int(tx), int(ty), r, g, b)
        
        # Draw Rods
        self.draw_line(canvas, int(self.cx), int(self.cy), int(x1), int(y1), 80, 80, 80)
        self.draw_line(canvas, int(x1), int(y1), int(x2), int(y2), 80, 80, 80)
        
        # Draw Pivot
        self.draw_filled_circle(canvas, int(self.cx), int(self.cy), 2, 80, 80, 80)
        
        # Draw Mass 1 (White/Grey)
        self.draw_filled_circle(canvas, int(x1), int(y1), 3, 200, 200, 200)
        
        # Draw Mass 2 (Red/Pink highlight)
        self.draw_filled_circle(canvas, int(x2), int(y2), 3, 255, 50, 50)
        
    def draw_filled_circle(self, canvas, cx, cy, radius, r, g, b):
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if 0 <= x < self.width and 0 <= y < self.height:
                    if (x - cx)**2 + (y - cy)**2 <= radius**2:
                        canvas.SetPixel(x, y, r, g, b)

    def draw_line(self, canvas, x0, y0, x1, y1, r, g, b):
        # Bresenham's Line Algorithm
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            if 0 <= x0 < self.width and 0 <= y0 < self.height:
                canvas.SetPixel(x0, y0, r, g, b)
            
            if x0 == x1 and y0 == y1:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
