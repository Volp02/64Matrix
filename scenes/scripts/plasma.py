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
        from PIL import Image
        
        t = self.time_tracker
        # Render at low resolution (1/4 size) for performance
        low_w, low_h = 16, 16
        
        scale1 = 0.2  # Adjusted scales for lower res
        scale2 = 0.12
        scale3 = 0.28
        
        # Pre-calculate row and column components
        v1_row = [math.sin(x * scale1 + t) for x in range(low_w)]
        v2_col = [math.sin((y * scale2) + t * 0.5) for y in range(low_h)]
        
        sin_t2 = math.sin(t/2)
        cos_t3 = math.cos(t/3)
        
        pixels = []
        
        for y in range(low_h):
            row_v2 = v2_col[y]
            y_part_v4 = y * cos_t3
            
            for x in range(low_w):
                # Component 1
                v1 = v1_row[x]
                
                # Component 2
                v2 = row_v2
                
                # Component 3 (Distance approx)
                # Recalculate dist on fly for low res is fast enough, no need for cache
                dx = x - 8 # centered
                dy = y - 8
                dist = math.sqrt(dx*dx + dy*dy)
                v3 = math.sin(dist * scale3 - t * 1.5)
                
                # Component 4
                v4 = math.sin((x * sin_t2 + y_part_v4) * 0.15 + t)

                # Sum components
                v = (v1 + v2 + v3 + v4) / 4.0
                
                # Map to color (0 to 1)
                val = (v + 1.0) / 2.0
                
                # Simple palette mapping
                r = int((math.sin(val * math.pi * 2 + t) + 1) * 127.5)
                g = int((math.sin(val * math.pi * 2 + t + 2.09) + 1) * 127.5)
                b = int((math.sin(val * math.pi * 2 + t + 4.18) + 1) * 127.5)
                
                pixels.append((r, g, b))
                
        # Create image from pixels
        img_low = Image.new('RGB', (low_w, low_h))
        img_low.putdata(pixels)
        
        # Upscale with bicubic interpolation (smooths out the blocks)
        img_high = img_low.resize((self.width, self.height), Image.BICUBIC)
        
        canvas.SetImage(img_high)
