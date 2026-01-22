from app.core.base_scene import BaseScene
import random

class BouncingBall(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.x = 10.0
        self.y = 10.0
        self.vx = 20.0 # pixels per second
        self.vy = 15.0
        self.radius = 2
        self.color = (255, 0, 0)
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Bounce X
        if self.x <= 0 or self.x >= self.width:
            self.vx *= -1
            self.x = max(0, min(self.x, self.width))
            self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            
        # Bounce Y
        if self.y <= 0 or self.y >= self.height:
            self.vy *= -1
            self.y = max(0, min(self.y, self.height))
            self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    def draw(self, canvas):
        # canvas.Clear() # Engine does this, but we can do it too if we want manual control
        
        # Draw Ball
        # Simple pixel drawing for a small ball
        ix = int(self.x)
        iy = int(self.y)
        canvas.SetPixel(ix, iy, self.color[0], self.color[1], self.color[2])
        canvas.SetPixel(ix+1, iy, self.color[0], self.color[1], self.color[2])
        canvas.SetPixel(ix, iy+1, self.color[0], self.color[1], self.color[2])
        canvas.SetPixel(ix+1, iy+1, self.color[0], self.color[1], self.color[2])
