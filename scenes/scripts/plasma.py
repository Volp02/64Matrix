from app.core.base_scene import BaseScene
import math

class Plasma(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.time_tracker = 0.0
        
        # Pre-compute distance grid for component 3
        self.dist_grid = [[0.0 for x in range(self.width)] for y in range(self.height)]
        cx = self.width / 2
        cy = self.height / 2
        for y in range(self.height):
            for x in range(self.width):
                dx = x - cx
                dy = y - cy
                self.dist_grid[y][x] = math.sqrt(dx*dx + dy*dy)

    def update(self, dt):
        self.time_tracker += dt

    def draw(self, canvas):
        t = self.time_tracker
        w = self.width
        h = self.height
        
        scale1 = 0.05
        scale2 = 0.03
        scale3 = 0.07
        
        # Pre-calculate row and column components
        # v1 depends only on x
        v1_row = [math.sin(x * scale1 + t) for x in range(w)]
        
        # v2 depends only on y
        v2_col = [math.sin((y * scale2) + t * 0.5) for y in range(h)]
        
        # v4 helpers
        sin_t2 = math.sin(t/2)
        cos_t3 = math.cos(t/3)
        
        for y in range(h):
            row_v2 = v2_col[y]
            row_dist = self.dist_grid[y]
            y_part_v4 = y * cos_t3
            
            for x in range(w):
                # Component 1 (Cached)
                v1 = v1_row[x]
                
                # Component 2 (Cached)
                v2 = row_v2
                
                # Component 3 (Distance cached)
                v3 = math.sin(row_dist[x] * scale3 - t * 1.5)
                
                # Component 4 (Simplified)
                # v4 = math.sin((x * math.sin(t/2) + y * math.cos(t/3)) * 0.04 + t)
                v4 = math.sin((x * sin_t2 + y_part_v4) * 0.04 + t)

                # Sum components
                v = (v1 + v2 + v3 + v4) / 4.0
                
                # Map to color (0 to 1)
                val = (v + 1.0) / 2.0
                
                # Simple palette mapping (performant)
                # R: shifted 0
                # G: shifted 1/3
                # B: shifted 2/3
                r = int((math.sin(val * math.pi * 2 + t) + 1) * 127.5)
                g = int((math.sin(val * math.pi * 2 + t + 2.09) + 1) * 127.5)
                b = int((math.sin(val * math.pi * 2 + t + 4.18) + 1) * 127.5)
                
                canvas.SetPixel(x, y, r, g, b)
