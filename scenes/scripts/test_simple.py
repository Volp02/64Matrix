from app.core.base_scene import BaseScene
import random

class TestSimple(BaseScene):
    """
    Very simple test animation to verify the system works.
    Just draws a moving colored square.
    """
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.x = self.width // 2
        self.y = self.height // 2
        self.vx = 30.0  # pixels per second
        self.vy = 25.0
        self.size = 5
        self.color = (255, 0, 0)  # Red
        
    def update(self, dt):
        # Get speed multiplier
        settings = self.state_manager.get_settings()
        speed_mult = settings.get("speed", 1.0)
        
        # Move
        self.x += self.vx * dt * speed_mult
        self.y += self.vy * dt * speed_mult
        
        # Bounce off walls
        if self.x - self.size <= 0 or self.x + self.size >= self.width:
            self.vx *= -1
            self.x = max(self.size, min(self.x, self.width - self.size))
            # Change color on bounce
            self.color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
            
        if self.y - self.size <= 0 or self.y + self.size >= self.height:
            self.vy *= -1
            self.y = max(self.size, min(self.y, self.height - self.size))
            self.color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )

    def draw(self, canvas):
        # Draw a filled square
        r, g, b = self.color
        center_x = int(self.x)
        center_y = int(self.y)
        
        for dy in range(-self.size, self.size + 1):
            for dx in range(-self.size, self.size + 1):
                px = center_x + dx
                py = center_y + dy
                if 0 <= px < self.width and 0 <= py < self.height:
                    canvas.SetPixel(px, py, r, g, b)
