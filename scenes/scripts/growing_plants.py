from app.core.base_scene import BaseScene
import random
import math

class Bug:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-10, 10)
        self.vy = random.uniform(-10, 10)
        self.timer = random.uniform(0, 100)
        self.off_screen_timer = 0.0
        
    def update(self, dt, target_x, target_y):
        self.timer += dt
        
        # Swirling motion (attracted to target, but orbiting)
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 1.0: dist = 1.0
        
        # Attraction
        self.vx += (dx / dist) * 50.0 * dt
        self.vy += (dy / dist) * 50.0 * dt
        
        # Perpendicular Orbit force
        self.vx += -(dy / dist) * 80.0 * dt
        self.vy += (dx / dist) * 80.0 * dt
        
        # Random noise
        self.vx += random.uniform(-20, 20) * dt
        self.vy += random.uniform(-20, 20) * dt
        
        # Damping
        self.vx *= 0.98
        self.vy *= 0.98
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Off-screen logic
        margin = 10
        if self.x < -margin or self.x > 64+margin or self.y < -margin or self.y > 64+margin:
            self.off_screen_timer += dt
            
            # 1. Steer back towards center
            to_center_x = 32 - self.x
            to_center_y = 32 - self.y
            dist_c = math.sqrt(to_center_x**2 + to_center_y**2)
            if dist_c > 0:
                # Strong pull back
                self.vx += (to_center_x / dist_c) * 150.0 * dt
                self.vy += (to_center_y / dist_c) * 150.0 * dt
            
            # 2. Respawn if gone too long
            if self.off_screen_timer > random.uniform(2.0, 4.0):
                self.respawn()
        else:
            self.off_screen_timer = 0.0

    def respawn(self):
        # Pick a random edge
        side = random.randint(0, 3)
        if side == 0: # Top
            self.x = random.uniform(0, 64)
            self.y = -5
            self.vy = random.uniform(5, 15)
            self.vx = random.uniform(-5, 5)
        elif side == 1: # Bottom
            self.x = random.uniform(0, 64)
            self.y = 69
            self.vy = random.uniform(-15, -5)
            self.vx = random.uniform(-5, 5)
        elif side == 2: # Left
            self.x = -5
            self.y = random.uniform(0, 64)
            self.vx = random.uniform(5, 15)
            self.vy = random.uniform(-5, 5)
        else: # Right
            self.x = 69
            self.y = random.uniform(0, 64)
            self.vx = random.uniform(-15, -5)
            self.vy = random.uniform(-5, 5)
            
        self.off_screen_timer = 0.0

    def draw(self, canvas):
        # Pulsing brightness
        pulse = (math.sin(self.timer * 10.0) + 1.0) / 2.0 # 0 to 1
        r, g, b = self.color
        # Add white flash
        r = min(255, int(r + pulse * 100))
        g = min(255, int(g + pulse * 100))
        b = min(255, int(b + pulse * 100))
        
        canvas.SetPixel(int(self.x), int(self.y), r, g, b)

class Leaf:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = 0.0
        self.target_size = random.uniform(1.5, 3.0)
        self.angle = random.uniform(0, math.pi*2)
        
    def update(self, dt):
        if self.size < self.target_size:
            self.size += dt * 3.0

class Offshoot:
    def __init__(self, x, y, angle, color):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.angle = angle
        self.color = color
        self.target_len = random.uniform(4, 12)
        self.current_len = 0.0
        self.points = [(x,y)]
        self.leaves = []
        self.growing = True

    def update(self, dt):
        if not self.growing:
            for l in self.leaves: l.update(dt)
            return

        self.current_len += dt * 10.0
        # Wiggle angle
        self.angle += math.sin(self.current_len * 0.5) * 0.1
        
        nx = self.start_x + math.cos(self.angle) * self.current_len
        ny = self.start_y + math.sin(self.angle) * self.current_len
        self.points.append((nx, ny))
        
        if self.current_len >= self.target_len:
            self.growing = False
            self.leaves.append(Leaf(nx, ny, (random.randint(40,100), random.randint(180,255), 40)))

    def draw(self, canvas, time):
        r, g, b = self.color
        for p in self.points:
            wind = get_wind(p[1], time)
            offset_p = (p[0] + wind, p[1])
            if 0 <= int(offset_p[0]) < 64 and 0 <= int(offset_p[1]) < 64:
                 canvas.SetPixel(int(offset_p[0]), int(offset_p[1]), r, g, b)
        
        for l in self.leaves:
            wind = get_wind(l.y, time)
            # Draw leaf manually with offset
            s = int(l.size)
            if s==0: continue
            cx, cy = int(l.x + wind), int(l.y)
            clr = l.color
            for dy in range(-s, s+1):
                for dx in range(-s, s+1):
                    if abs(dx)+abs(dy)<=s: 
                         if 0 <= cx+dx < 64 and 0 <= cy+dy < 64:
                             canvas.SetPixel(cx+dx, cy+dy, *clr)

    def draw_shadow(self, canvas, offset_x, offset_y, time, shadow_color):
         for p in self.points:
            wind = get_wind(p[1], time)
            canvas.SetPixel(int(p[0] + wind) + offset_x, int(p[1]) + offset_y, *shadow_color)
         for l in self.leaves:
            wind = get_wind(l.y, time)
            s = int(l.size)
            if s==0: continue
            cx, cy = int(l.x + wind)+offset_x, int(l.y)+offset_y
            for dy in range(-s, s+1):
                 for dx in range(-s, s+1):
                     if abs(dx)+abs(dy)<=s: canvas.SetPixel(cx+dx, cy+dy, *shadow_color)

def get_wind(y, time):
    height_factor = max(0.0, (64.0 - y) / 64.0)
    return math.sin(time * 1.5 + y * 0.05) * 4.0 * (height_factor ** 2)

class Vine:
    def __init__(self, x, trellis_x):
        self.points = []
        self.x = x
        self.y = 63.0
        self.trellis_x = trellis_x 
        
        self.color = (random.randint(40, 80), random.randint(150, 220), 40)
        self.growth_speed = random.uniform(5.0, 10.0) # Slower growth
        self.angle_offset = random.uniform(0, math.pi * 2)
        
        # Tighter wrap for fence
        self.wrap_freq = 0.2
        self.wrap_amp = 3.0
        
        self.grow_active = True
        self.leaves = [] 
        self.offshoots = [] # Added offshoots list
        self.leaf_timer = 0.0

    def update(self, dt):
        for l in self.leaves: l.update(dt)
        for o in self.offshoots: o.update(dt)

        if not self.grow_active:
            return

        self.y -= self.growth_speed * dt
        self.x = self.trellis_x + math.sin(self.y * self.wrap_freq + self.angle_offset) * self.wrap_amp
        self.points.append((self.x, self.y))
        
        if self.y < 5:
            self.grow_active = False
            
        self.leaf_timer += dt
        if self.leaf_timer > 0.2: 
            self.leaf_timer = 0
            if random.random() < 0.6: # 60% chance spawn
                 if random.random() < 0.5: # 50% branch
                     angle = random.uniform(-math.pi, 0)
                     self.offshoots.append(Offshoot(self.x, self.y, angle, self.color))
                 else:
                     self.leaves.append(Leaf(self.x, self.y, (random.randint(40,100), random.randint(180,255), 40)))



    def draw_shadow(self, canvas, offset_x, offset_y, time):
        # Shadow color (Darker Yellow/Brownish)
        shadow_color = (200, 200, 160)
        
        for p in self.points:
            wind = get_wind(p[1], time)
            canvas.SetPixel(int(p[0] + wind) + offset_x, int(p[1]) + offset_y, *shadow_color)
        
        for o in self.offshoots:
            o.draw_shadow(canvas, offset_x, offset_y, time, shadow_color)
            
        for l in self.leaves:
            wind = get_wind(l.y, time)
            s = int(l.size)
            cx, cy = int(l.x + wind)+offset_x, int(l.y)+offset_y
            for dy in range(-s, s+1):
                for dx in range(-s, s+1):
                    if abs(dx)+abs(dy)<=s: canvas.SetPixel(cx+dx, cy+dy, *shadow_color)

    def draw(self, canvas, time):
        r, g, b = self.color
        tx = self.trellis_x
        
        for i in range(len(self.points)):
            p = self.points[i]
            wind = get_wind(p[1], time)
            
            px = p[0] + wind
            py = p[1]
            
            # Depth check
            angle = py * self.wrap_freq + self.angle_offset
            z = math.cos(angle)
            ix, iy = int(px), int(py)
            
            if ix == tx and z < 0:
                continue
                
            if 0 <= ix < 64 and 0 <= iy < 64:
                 canvas.SetPixel(ix, iy, r, g, b)
        
        for o in self.offshoots:
            o.draw(canvas, time)
                 
        for l in self.leaves:
            wind = get_wind(l.y, time)
            s = int(l.size)
            cx, cy = int(l.x + wind), int(l.y)
            clr = l.color
            for dy in range(-s, s+1):
                for dx in range(-s, s+1):
                    if abs(dx)+abs(dy)<=s: 
                         if 0 <= cx+dx < 64 and 0 <= cy+dy < 64:
                             canvas.SetPixel(cx+dx, cy+dy, *clr)

class GrowingPlants(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.reset()
        
    def get_palette(self):
        try:
            palette_mgr = getattr(self.state_manager, '_palette_manager', None)
            if palette_mgr:
                return self.state_manager.get_palette_colors(palette_mgr)
        except:
            pass
        return None

    def reset(self):
        self.posts = [16, 32, 48]
        self.vines = [Vine(px, px) for px in self.posts]
        self.time = 0.0
        
        # Bug Setup
        self.bugs = []
        palette = self.get_palette()
        
        # 5 Bugs
        for i in range(5):
            # Pick color from palette or random
            if palette and len(palette) > 0:
                color = random.choice(palette)
            else:
                color = (
                    random.randint(100, 255),
                    random.randint(100, 255),
                    random.randint(100, 255)
                )
            # Random pos intensity
            self.bugs.append(Bug(
                random.uniform(10, 54),
                random.uniform(10, 54),
                color
            ))
        
        # Pre-generate background wall texture (static noise)
        self.bg_texture = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Subtle variation: +/- 15
                noise = random.randint(-15, 15)
                row.append(noise)
            self.bg_texture.append(row)
            
        # Pre-generate ground/soil
        self.ground_pixels = []
        for x in range(self.width):
            # Uneven ground height 2-5
            h = random.randint(2, 5)
            for i in range(h):
                y = self.height - 1 - i
                # Earthy/Grassy colors
                if i == h - 1: # Top pixel is grassy
                     col = (random.randint(20, 50), random.randint(60, 100), 20)
                else: # Soil
                     col = (random.randint(30, 50), random.randint(30, 50), 20)
                self.ground_pixels.append((x, y, col))

    def update(self, dt):
        self.time += dt
        for v in self.vines: v.update(dt)
        for b in self.bugs: 
            target = self.vines[1]
            b.update(dt, target.x, target.y)
            
        if self.time > 20.0:
            self.reset()
            
    def draw(self, canvas):
        # 1. Textured Wall Background
        # Base color: Light Sunny Yellow (255, 250, 200)
        base_r, base_g, base_b = 255, 250, 200
        
        for y in range(self.height):
            row = self.bg_texture[y]
            for x in range(self.width):
                n = row[x]
                # Apply texture offset
                r = max(0, min(255, base_r + n))
                g = max(0, min(255, base_g + n))
                b = max(0, min(255, base_b + n))
                canvas.SetPixel(x, y, r, g, b)
        
        # 2. Shadows (Offset +3, +3)
        off_x, off_y = 3, 3
        
        # Fence Shadows
        for px in self.posts:
            for y in range(self.height):
                if y < self.height - 4: # Don't draw shadow under ground
                    canvas.SetPixel(px+off_x, y+off_y, 200, 200, 160)
        # Vine Shadows
        for v in self.vines:
            v.draw_shadow(canvas, off_x, off_y, self.time)
            
        # 3. Fence (Foreground)
        for px in self.posts:
            for y in range(self.height):
                canvas.SetPixel(px, y, 100, 100, 80) # Brownish post
        
        # 4. Ground (Covering bottom of fence)
        for gp in self.ground_pixels:
             canvas.SetPixel(gp[0], gp[1], *gp[2])
                
        # 5. Vines (Foreground - growing out of ground)
        for v in self.vines:
            v.draw(canvas, self.time)
            
        # 6. Bugs
        for b in self.bugs:
            b.draw(canvas)
