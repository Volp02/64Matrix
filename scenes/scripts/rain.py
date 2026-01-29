from app.core.base_scene import BaseScene
import random
import math
from PIL import Image, ImageDraw

class Splash:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.life = 1.0 # 0.0 to 1.0
        self.radius = 0.0
        
    def update(self, dt):
        self.life -= dt * 4.0 # Fast fade
        self.radius += dt * 5.0

class Rain(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.drops = []
        self.splashes = []
        self.width = matrix.width
        self.height = matrix.height
        
        # 3. Generate Clouds (Dynamic)
        self.clouds = []
        for _ in range(5):
            self.clouds.append({
                'x': random.uniform(0, 64),
                'y': random.uniform(0, 30),
                'w': random.uniform(20, 40),
                'h': random.uniform(10, 20),
                'speed': random.uniform(2.0, 5.0)
            })
            
        # Pre-render static background (Sky + Skyline + Street)
        self.background_img = self._prerender_background()

    def _prerender_background(self):
        """Pre-render static elements to a PIL Image"""
        img = Image.new('RGB', (self.width, self.height), (0, 0, 15)) # Sky color
        draw = ImageDraw.Draw(img)
        pixels = img.load()
        
        # 1. Generate City Skyline (Silhouette)
        horizon = 49
        current_x = 0
        while current_x < self.width:
            w = random.randint(3, 8)
            h = random.randint(15, 45) # Taller buildings
            
            for bx in range(current_x, min(current_x + w, self.width)):
                for by in range(h, horizon):
                    color = (0, 0, 5) # Almost black
                    # Random window
                    if random.random() < 0.05 and bx % 2 == 0 and by % 3 == 0:
                         color = (50, 50, 20) # Dim yellow light
                    pixels[bx, by] = color
            current_x += w
            
        # 2. Generate Street Texture
        for y in range(horizon, self.height):
            for x in range(self.width):
                base = 20
                var = random.randint(-2, 2)
                val = max(0, min(255, base + var))
                color = (val, val, val + 5) 
                pixels[x, y] = color
                
        return img

    def update(self, dt):
        # Update Clouds
        for c in self.clouds:
            c['x'] += c['speed'] * dt
            if c['x'] - c['w'] > self.width:
                c['x'] = -c['w']
                
        # Spawn Rain
        if random.random() < 0.6: 
            num = random.randint(1, 2)
            for _ in range(num):
                self.spawn_drop()
                
        # Update drops
        active_drops = []
        for d in self.drops:
            d['y'] += d['speed'] * dt
            
            # Ground hit logic
            if d['layer'] == 1:
                ground_y = d['ground_y'] 
            else:
                ground_y = self.height - 1
            
            if d['y'] >= ground_y:
                self.splashes.append(Splash(d['x'], ground_y, d['color']))
            else:
                active_drops.append(d)
        self.drops = active_drops
        
        # Update Splashes
        active_splashes = []
        for s in self.splashes:
            s.update(dt)
            if s.life > 0:
                active_splashes.append(s)
        self.splashes = active_splashes

    def spawn_drop(self):
        layer = random.randint(0, 1)
        
        if layer == 0: # Front
            speed = random.uniform(50, 70)
            length = random.randint(2, 4)
            color = (180, 200, 255) 
            x = random.randint(0, self.width-1)
            ground_y = self.height - 1
        else: # Back
            speed = random.uniform(30, 45)
            length = random.randint(1, 2)
            color = (50, 80, 150) 
            x = random.randint(0, self.width-1)
            ground_y = random.randint(49, 60)
            
        self.drops.append({
            'x': x,
            'y': -length,
            'speed': speed,
            'length': length,
            'color': color,
            'layer': layer,
            'ground_y': ground_y
        })

    def draw(self, canvas):
        # Start with static background
        img = self.background_img.copy()
        draw = ImageDraw.Draw(img)
        
        # 1.5 Clouds (Barely visible)
        cloud_color = (15, 15, 30)
        for c in self.clouds:
            cx, cy = c['x'], c['y']
            rx, ry = c['w']/2, c['h']/2
            # Bounding box for ellipse
            bbox = [cx - rx, cy - ry, cx + rx, cy + ry]
            
            # Since update logic wraps x, we need to draw potentially twice for seamless wrapping
            # Or just rely on the fact that bbox can handle off-screen coords
            draw.ellipse(bbox, fill=cloud_color)
            
            # Wrap handling simply
            if c['x'] + rx > self.width:
                # Draw wrap-around part
                bbox_wrap = [cx - rx - self.width, cy - ry, cx + rx - self.width, cy + ry]
                draw.ellipse(bbox_wrap, fill=cloud_color)

        # 4. Rain Matches
        for d in self.drops:
            x = int(d['x'])
            y = int(d['y'])
            l = d['length']
            color = d['color']
            
            # Simple line
            draw.line([(x, y), (x, y - l)], fill=color, width=1)
                    
        # 5. Splashes
        for s in self.splashes:
            if s.life <= 0: continue
            
            r, g, b = s.color
            # Fade color
            r = int(r * s.life)
            g = int(g * s.life)
            b = int(b * s.life)
            color = (r, g, b)
            
            rad = int(s.radius)
            if rad == 0:
                draw.point((int(s.x), int(s.y)), fill=color)
            else:
                # Small droplet spray
                draw.point((int(s.x - rad), int(s.y - 1)), fill=color)
                draw.point((int(s.x + rad), int(s.y - 1)), fill=color)

        canvas.SetImage(img)
