from app.core.base_scene import BaseScene
import random
import math

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
        
    def draw(self, canvas):
        if self.life <= 0: return
        
        # Simple small expanding ring or just pixels
        r, g, b = self.color
        # Fade color
        r = int(r * self.life)
        g = int(g * self.life)
        b = int(b * self.life)
        
        rad = int(self.radius)
        # Draw pixels around center
        # Splash is small, usually just 1 or 2 px out
        if rad == 0:
            canvas.SetPixel(int(self.x), int(self.y), r, g, b)
        else:
            # Draw Left/Right/Up small droplets
            canvas.SetPixel(int(self.x - rad), int(self.y - 1), r, g, b)
            canvas.SetPixel(int(self.x + rad), int(self.y - 1), r, g, b)

class Rain(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.drops = []
        self.splashes = []
        self.width = matrix.width
        self.height = matrix.height
        
        # 1. Generate City Skyline (Silhouette)
        # Horizon is at Y=49 (Lowered by 4 pixels from 45)
        horizon = 49
        self.skyline = [] # List of (x, y_start, y_end, color)
        
        current_x = 0
        while current_x < self.width:
            # Building width
            w = random.randint(3, 8)
            # Building height (top Y)
            h = random.randint(15, 45) # Taller buildings
            
            # Add building columns
            for bx in range(current_x, min(current_x + w, self.width)):
                # Wall
                for by in range(h, horizon):
                    color = (0, 0, 5) # Almost black
                    
                    # Random window?
                    if random.random() < 0.05 and bx % 2 == 0 and by % 3 == 0:
                         color = (50, 50, 20) # Dim yellow light
                         
                    self.skyline.append((bx, by, color))
            
            current_x += w
            
        # 2. Generate Street Texture (Darker, Less Texture)
        self.street_pixels = []
        for y in range(horizon, self.height):
            for x in range(self.width):
                # Dark Grey, very smooth
                base = 20
                var = random.randint(-2, 2) # Minimal noise
                val = max(0, min(255, base + var))
                color = (val, val, val + 5) 
                self.street_pixels.append((x, y, color))
                
        # 3. Generate Clouds (Background)
        self.clouds = []
        for _ in range(5):
            self.clouds.append({
                'x': random.uniform(0, 64),
                'y': random.uniform(0, 30),
                'w': random.uniform(20, 40),
                'h': random.uniform(10, 20),
                'speed': random.uniform(2.0, 5.0)
            })

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
        canvas.Clear()
        
        # 1. Sky (Deep Midnight Blue)
        canvas.Fill(0, 0, 15)
        
        # 1.5 Clouds (Barely visible)
        cloud_color = (15, 15, 30) # Slightly lighter/greyer than sky
        for c in self.clouds:
            # Simple ellipse
            cx, cy = int(c['x']), int(c['y'])
            rx, ry = int(c['w']/2), int(c['h']/2)
            
            # Bounding box optimization
            for y in range(cy-ry, cy+ry):
                for x in range(cx-rx, cx+rx):
                    # Check ellipse
                    if ((x-cx)**2)/(rx**2) + ((y-cy)**2)/(ry**2) <= 1.0:
                        # Wrap x for drawing? simplest is just draw if visible
                        # Our update loop wraps, so just draw normal check boundaries
                        draw_x = x % self.width # Wrap for seamless
                        if 0 <= y < self.height:
                             canvas.SetPixel(draw_x, y, *cloud_color)
        
        # 2. City Silhouette
        for p in self.skyline:
             canvas.SetPixel(p[0], p[1], p[2][0], p[2][1], p[2][2])
        
        # 3. Street (Bottom)
        for p in self.street_pixels:
            canvas.SetPixel(p[0], p[1], p[2][0], p[2][1], p[2][2])
        
        # 4. Rain & Splashes
        for d in self.drops:
            x = int(d['x'])
            y = int(d['y'])
            l = d['length']
            r, g, b = d['color']
            for i in range(l):
                draw_y = y - i
                if 0 <= draw_y < self.height:
                    canvas.SetPixel(x, int(draw_y), r, g, b)
                    
        for s in self.splashes:
            s.draw(canvas)
