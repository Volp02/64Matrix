from app.core.base_scene import BaseScene
import math
import random

class Aurora(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.time = 0.0
        
        # Wave Parameters
        # A list of interference waves to sum up
        self.waves = [
            {'freq': 0.1, 'speed': 0.5, 'amp': 10.0, 'phase': 0.0},
            {'freq': 0.2, 'speed': -0.3, 'amp': 5.0, 'phase': 1.0},
             {'freq': 0.05, 'speed': 0.2, 'amp': 15.0, 'phase': 2.0},
        ]
        
        # Star Parameters (Barely visible sparkling stars)
        self.stars = []
        for _ in range(30): # 30 stars
            self.stars.append({
                'x': random.randint(0, 63),
                'y': random.randint(0, 63),
                'phase': random.uniform(0, math.pi * 2),
                'speed': random.uniform(2.0, 5.0)
            })
        
    def update(self, dt):
        self.time += dt
        # No motion for stars, just twinkle based on time

    def draw(self, canvas):
        # 1. Dark Blue Background
        bg_color = (0, 10, 30)
        canvas.Fill(*bg_color)
        
        # 2. Draw Stars (and track them for blending)
        star_map = {}
        
        for s in self.stars:
            # Twinkle: Sine wave of brightness
            # Barely visible: Base (20), Peak (80-100)
            brightness = (math.sin(self.time * s['speed'] + s['phase']) + 1.0) * 0.5 # 0-1
            val = int(20 + brightness * 60) # Range 20-80
            
            # Draw
            color = (val, val, val + 20) # Blue-ish white
            canvas.SetPixel(s['x'], s['y'], *color)
            
            # Store in map for blending
            star_map[(s['x'], s['y'])] = color
        
        # 3. Draw Aurora Curtain
        for x in range(self.width):
            base_y = 32.0 
            for w in self.waves:
                base_y += math.sin(x * w['freq'] + self.time * w['speed'] + w['phase']) * w['amp']
                
            center_y = int(base_y)
            curtain_h = 25
            
            for y in range(center_y - curtain_h, center_y + curtain_h):
                if 0 <= y < self.height:
                    dist = abs(y - center_y)
                    norm_dist = dist / curtain_h
                    
                    if norm_dist < 1.0:
                        intensity = 1.0 - (norm_dist ** 1.5) 
                        val = int(255 * intensity)
                        rel_y = y - center_y
                        
                        r, g, b = 0, 0, 0
                        if rel_y > 0: 
                            # Bottom: Green
                            g = val
                            b = int(val * 0.2)
                        else:
                            # Top: Purple/Pink
                            f = abs(rel_y / curtain_h)
                            r = int(val * f * 0.8) 
                            g = int(val * (1.0 - f * 0.5)) 
                            b = int(val * f) 
                            
                        # BLENDING
                        # Default to clean sky color
                        target_bg_r, target_bg_g, target_bg_b = bg_color
                        
                        # Check if over a star
                        if (x, y) in star_map:
                             target_bg_r, target_bg_g, target_bg_b = star_map[(x, y)]
                        
                        alpha = intensity * 0.8 
                        out_r = int(r * alpha + target_bg_r * (1.0 - alpha))
                        out_g = int(g * alpha + target_bg_g * (1.0 - alpha))
                        out_b = int(b * alpha + target_bg_b * (1.0 - alpha))
                        
                        canvas.SetPixel(x, y, out_r, out_g, out_b)
