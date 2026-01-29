from app.core.base_scene import BaseScene
import random
import math
from PIL import Image, ImageDraw

class Flame:
    """Persistent flame that flickers in place - never disappears"""
    def __init__(self, x, y, intensity=1.0):
        self.base_x = float(x)
        self.base_y = float(y)
        self.x = float(x)
        self.intensity = intensity
        
        # Flame dimensions - vary over time
        self.base_height = random.uniform(8, 16)
        self.current_height = self.base_height
        self.base_width = random.uniform(3.0, 5.0)
        
        # Multiple phase offsets for organic movement
        self.height_phase = random.uniform(0, math.pi * 2)
        self.width_phase = random.uniform(0, math.pi * 2)
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.brightness_phase = random.uniform(0, math.pi * 2)
        
        # Animation speeds (different for each property)
        self.height_speed = random.uniform(3, 6)
        self.width_speed = random.uniform(4, 7)
        self.sway_speed = random.uniform(2, 4)  # Slower horizontal sway
        self.brightness_speed = random.uniform(5, 10)
        
        # Horizontal sway amount - MORE sway
        self.sway_amount = random.uniform(2.5, 4.5)
        
    def update(self, dt):
        # Update all phases
        self.height_phase += self.height_speed * dt
        self.width_phase += self.width_speed * dt
        self.sway_phase += self.sway_speed * dt
        self.brightness_phase += self.brightness_speed * dt
        
        # Height varies but never goes below minimum
        height_variation = math.sin(self.height_phase) * 0.4 + math.sin(self.height_phase * 1.7) * 0.2
        self.current_height = self.base_height * (0.6 + 0.4 * (height_variation + 1) / 2)
        self.current_height = max(4, self.current_height)  # Minimum height of 4
        
        # Horizontal sway - smooth side to side motion
        sway = math.sin(self.sway_phase) * self.sway_amount
        sway += math.sin(self.sway_phase * 0.7) * self.sway_amount * 0.3  # Secondary wobble
        self.x = self.base_x + sway
        
    def is_alive(self):
        return True
    
    def get_current_width(self, rel_height):
        """Get width at a given height, with flickering"""
        # Width varies over time
        width_variation = math.sin(self.width_phase + rel_height * 2) * 0.25 + 0.75
        
        # Taper toward tip
        taper = 1.0 - rel_height * 0.6
        
        return self.base_width * width_variation * taper
    
    def get_brightness(self):
        """Get current brightness multiplier"""
        # Flicker between 0.6 and 1.0 - never too dim
        flicker = math.sin(self.brightness_phase) * 0.2 + math.sin(self.brightness_phase * 2.3) * 0.1
        return 0.7 + flicker * 0.5
    
    def get_color_at_height(self, rel_height):
        """Get flame color based on relative height (0=base, 1=tip)"""
        brightness = self.get_brightness() * self.intensity
        
        if rel_height < 0.25:
            # Base: bright white-yellow (hottest)
            r = int(255 * brightness)
            g = int(245 * brightness)
            b = int(200 * brightness)
        elif rel_height < 0.45:
            # Lower: bright yellow
            r = int(255 * brightness)
            g = int(210 * brightness)
            b = int(80 * brightness)
        elif rel_height < 0.65:
            # Middle: orange
            r = int(255 * brightness)
            g = int(140 * brightness)
            b = int(30 * brightness)
        elif rel_height < 0.85:
            # Upper: red-orange
            r = int(240 * brightness)
            g = int(80 * brightness)
            b = int(15 * brightness)
        else:
            # Tip: darker red
            tip_fade = (rel_height - 0.85) / 0.15
            r = int(200 * brightness * (1 - tip_fade * 0.3))
            g = int(50 * brightness * (1 - tip_fade * 0.5))
            b = int(10 * brightness)
        
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


class Spark:
    """Spark flying up from fire"""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-25, 25)
        self.vy = random.uniform(-100, -60)
        self.life = random.uniform(0.4, 1.0)
        self.max_life = self.life
        
    def update(self, dt):
        self.vx += random.uniform(-40, 40) * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 35 * dt  # Gravity
        self.vx *= 0.95
        self.life -= dt
        
    def is_alive(self):
        return self.life > 0


class Smoke:
    """Smoke particle"""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-18, -10)
        self.life = random.uniform(2.0, 4.0)
        self.max_life = self.life
        self.wobble = random.uniform(0, math.pi * 2)
        
    def update(self, dt):
        self.wobble += dt * 2.0
        self.vx += math.sin(self.wobble) * 8 * dt
        self.vx *= 0.98
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        
    def is_alive(self):
        return self.life > 0 and self.y > -5


class WoodLog:
    """Angled wood log"""
    def __init__(self, x1, y1, x2, y2, thickness):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.thickness = thickness
        
        # Wood color
        self.base_color = (
            random.randint(40, 60),
            random.randint(25, 40),
            random.randint(10, 20)
        )
        self.char_level = random.uniform(0.3, 0.7)
        
        # Calculate pixels (Still used for spawn points/collisions)
        self.pixels = self._calculate_pixels()
        self.ember_phases = {p: random.uniform(0, math.pi * 2) for p in self.pixels}
        
        # Flame spawn points along the top edge
        self.spawn_points = self._calculate_spawn_points()
        
    def _calculate_pixels(self):
        """Calculate log pixels using line algorithm"""
        pixels = set()
        x1, y1 = int(self.x1), int(self.y1)
        x2, y2 = int(self.x2), int(self.y2)
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        center_line = []
        
        while True:
            center_line.append((x, y))
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        # Add thickness
        length = math.sqrt(dx*dx + dy*dy) if (dx > 0 or dy > 0) else 1
        perp_x = -dy / length if length > 0 else 0
        perp_y = dx / length if length > 0 else 1
        
        for px, py in center_line:
            for t in range(-self.thickness, self.thickness + 1):
                nx = int(px + perp_x * t)
                ny = int(py + perp_y * t)
                pixels.add((nx, ny))
        
        return pixels
    
    def _calculate_spawn_points(self):
        """Find points along top of log where flames can spawn"""
        points = []
        for px, py in self.pixels:
            # Check if this pixel has empty space above (top edge)
            if (px, py - 1) not in self.pixels:
                points.append((px, py - 1))
        return points
    
    def update_embers(self, dt):
        for p in self.ember_phases:
            self.ember_phases[p] += dt * random.uniform(5, 10)
    
    def get_pixel_color(self, px, py, fire_center_x):
        r = int(self.base_color[0] * (1 - self.char_level * 0.3))
        g = int(self.base_color[1] * (1 - self.char_level * 0.4))
        b = int(self.base_color[2] * (1 - self.char_level * 0.2))
        
        # Edge detection for ember glow
        is_edge = False
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (px + dx, py + dy) not in self.pixels:
                is_edge = True
                break
        
        if is_edge and (px, py) in self.ember_phases:
            dist = abs(px - fire_center_x) / 25.0
            center_factor = max(0, 1.0 - dist)
            
            phase = self.ember_phases[(px, py)]
            flicker = (math.sin(phase) * 0.5 + 0.5) * random.uniform(0.8, 1.2)
            
            # Top edges glow more
            is_top = (px, py - 1) not in self.pixels
            top_bonus = 1.3 if is_top else 0.7
            
            ember = flicker * self.char_level * center_factor * top_bonus
            
            if ember > 0.2:
                r = min(255, r + int(220 * ember))
                g = min(255, g + int(100 * ember))
                b = min(255, b + int(20 * ember))
        
        return (r, g, b)


class Fire(BaseScene):
    """
    Dynamic campfire with night scene background - trees, lake, stars.
    Optimized to use PIL for rendering.
    """
    
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        
        self.fire_center_x = self.width // 2
        self.fire_base_y = self.height - 10
        
        # Scene layout
        self.horizon_y = 28  # Where sky meets land/lake
        self.lake_start_y = self.horizon_y + 1
        self.lake_end_y = self.height - 12  # Lake ends before campfire area
        
        # Generate background elements
        self.stars = self._generate_stars()
        
        # Create wood arrangement
        self.logs = self._create_wood_arrangement()
        
        # Collect all flame spawn points from logs
        self.all_spawn_points = []
        for log in self.logs:
            self.all_spawn_points.extend(log.spawn_points)
        
        # Add some spawn points in the center (between logs)
        for i in range(8):
            x = self.fire_center_x + random.randint(-10, 10)
            y = self.fire_base_y - random.randint(0, 5)
            self.all_spawn_points.append((x, y))
        
        # Particles
        self.flames = []
        self.sparks = []
        self.smoke_particles = []
        
        # Timers
        self.time = 0.0
        self.flame_timer = 0.0
        self.spark_timer = 0.0
        self.smoke_timer = 0.0
        
        # Pre-render static background
        self.background_img = self._prerender_background()
    
    def _generate_stars(self):
        """Generate random star positions in the sky"""
        stars = []
        for _ in range(35):  # Number of stars
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.horizon_y - 5)
            # Storing color directly for performance
            brightness = random.uniform(0.4, 1.0)
            sr = int(255 * brightness)
            sg = int(250 * brightness)
            sb = int(220 * brightness)
            
            stars.append({
                'x': x,
                'y': y,
                'brightness': brightness,
                'color': (sr, sg, sb),
                'twinkle_speed': random.uniform(1.5, 4.0),
                'twinkle_phase': random.uniform(0, math.pi * 2)
            })
        return stars

    def _create_wood_arrangement(self):
        """Create campfire wood logs"""
        logs = []
        cx = self.fire_center_x
        base_y = self.fire_base_y
        
        # Back/bottom logs (flatter)
        logs.append(WoodLog(cx - 18, base_y + 6, cx + 16, base_y + 4, 2))
        logs.append(WoodLog(cx - 14, base_y + 5, cx + 20, base_y + 7, 2))
        
        # Angled logs leaning in from sides
        logs.append(WoodLog(cx - 22, base_y + 8, cx - 5, base_y - 6, 2))
        logs.append(WoodLog(cx + 20, base_y + 9, cx + 3, base_y - 8, 2))
        
        # Front crossing logs
        logs.append(WoodLog(cx - 18, base_y + 10, cx + 8, base_y - 2, 3))
        logs.append(WoodLog(cx + 16, base_y + 11, cx - 10, base_y + 0, 2))
        
        return logs

    def _prerender_background(self):
        """Pre-render static elements (Sky, Lake shape, Ground, Mountains)"""
        img = Image.new('RGB', (self.width, self.height))
        pixels = img.load()
        
        # 1. Sky Gradient
        for y in range(self.horizon_y):
            gradient = y / self.horizon_y
            sky_r = int(5 + gradient * 8)
            sky_g = int(8 + gradient * 12)
            sky_b = int(25 + gradient * 20)
            for x in range(self.width):
                pixels[x, y] = (sky_r, sky_g, sky_b)
                
        # 2. Lake and Ground
        # Generative lake shape
        lake_center_x = self.width // 2
        lake_center_y = (self.lake_start_y + self.lake_end_y) // 2
        lake_width = 22
        lake_height = (self.lake_end_y - self.lake_start_y) // 2
        
        for y in range(self.lake_start_y, self.height):
            for x in range(self.width):
                # Check for Lake
                in_lake = False
                if y < self.lake_end_y:
                    dx = (x - lake_center_x) / lake_width
                    dy = (y - lake_center_y) / max(1, lake_height)
                    noise = math.sin(x * 0.3) * 0.15 + math.sin(x * 0.7) * 0.1
                    dist = dx * dx + dy * dy + noise
                    if dist < 1.0:
                        in_lake = True
                
                if in_lake:
                    # Lake water - darker toward edges/bottom
                    depth = (y - self.lake_start_y) / max(1, self.lake_end_y - self.lake_start_y)
                    lake_r = int(4 + (1 - depth) * 6)
                    lake_g = int(6 + (1 - depth) * 10)
                    lake_b = int(20 + (1 - depth) * 18)
                    pixels[x, y] = (lake_r, lake_g, lake_b)
                else:
                    # Ground/shore - dark earth tones
                    pixels[x, y] = (10, 8, 5)

        # 3. Mountains
        # Mountain positions: (center_x, height, width_factor)
        mountain_data = [
            (5, 14, 1.2), (15, 20, 1.0), (25, 12, 0.9),
            (42, 15, 1.1), (52, 22, 1.0), (60, 11, 0.8),
        ]
        
        for center_x, height, width_factor in mountain_data:
            for y_offset in range(height):
                rel_height = y_offset / height
                width = int((1 + rel_height * height * 0.4) * width_factor)
                mountain_y = self.horizon_y - height + y_offset
                is_snow = rel_height < 0.25
                
                for dx in range(-width, width + 1):
                    mountain_x = center_x + dx
                    if 0 <= mountain_x < self.width and 0 <= mountain_y < self.height:
                        snow_threshold = 0.25 + random.uniform(-0.05, 0.05)
                        pixel_is_snow = rel_height < snow_threshold
                        
                        color = (45, 50, 55) if pixel_is_snow else (5, 5, 8)
                        pixels[mountain_x, mountain_y] = color
                        
        return img
    
    def enter(self, state_manager):
        """Create all flames - they persist forever"""
        self.flames = []
        for _ in range(50):
            self._spawn_flame()
    
    def _spawn_flame(self):
        """Spawn a new flame from a random spawn point"""
        if not self.all_spawn_points:
            return
            
        weights = []
        for x, y in self.all_spawn_points:
            dist = abs(x - self.fire_center_x)
            weight = max(0.3, 1.0 - dist / 25.0)
            weights.append(weight)
        
        # Weighted random selection
        # (Simplified logic for performance)
        chosen = random.choices(self.all_spawn_points, weights=weights, k=1)[0]
        
        x, y = chosen
        x += random.uniform(-1.5, 1.5)
        y += random.uniform(-1, 1)
        
        dist = abs(x - self.fire_center_x)
        intensity = max(0.5, 1.0 - dist / 30.0)
        intensity *= random.uniform(0.8, 1.2)
        
        self.flames.append(Flame(x, y, intensity))
    
    def _spawn_spark(self):
        if self.flames:
            flame = random.choice(self.flames)
            spark_y = flame.base_y - random.uniform(3, flame.current_height * 0.7)
            self.sparks.append(Spark(flame.x, spark_y))
    
    def _spawn_smoke(self):
        if self.flames:
            flame = random.choice(self.flames)
            smoke_y = flame.base_y - flame.current_height - 2
            self.smoke_particles.append(Smoke(flame.x + random.uniform(-3, 3), smoke_y))
    
    def update(self, dt):
        self.time += dt
        
        for flame in self.flames:
            flame.update(dt)
        if len(self.flames) < 50:
            self._spawn_flame()
        
        self.spark_timer += dt
        if self.spark_timer > 0.1:
            self.spark_timer = 0
            if random.random() < 0.4:
                self._spawn_spark()
        
        self.smoke_timer += dt
        if self.smoke_timer > 0.08:
            self.smoke_timer = 0
            if random.random() < 0.6:
                self._spawn_smoke()
        
        for spark in self.sparks:
            spark.update(dt)
        self.sparks = [s for s in self.sparks if s.is_alive()]
        
        for smoke in self.smoke_particles:
            smoke.update(dt)
        self.smoke_particles = [s for s in self.smoke_particles if s.is_alive()]
        
        for log in self.logs:
            log.update_embers(dt)
        
        for star in self.stars:
            star['twinkle_phase'] += star['twinkle_speed'] * dt
        
        if len(self.sparks) > 20: self.sparks = self.sparks[-20:]
        if len(self.smoke_particles) > 40: self.smoke_particles = self.smoke_particles[-40:]

    def draw(self, canvas):
        # Start with pre-rendered background
        img = self.background_img.copy()
        draw = ImageDraw.Draw(img)
        
        # 1. Update Stars (Draw over background)
        for star in self.stars:
            # Twinkle effect
            twinkle = (math.sin(star['twinkle_phase']) * 0.3 + 0.7)
            # Recompute color here to apply twinkle
            r = int(star['color'][0] * twinkle)
            g = int(star['color'][1] * twinkle)
            b = int(star['color'][2] * twinkle)
            draw.point((star['x'], star['y']), fill=(r, g, b))
            
            # Star reflections in lake (Simple Point check)
            # Assuming we know lake bounds roughly
            mirror_y = self.lake_start_y + (self.horizon_y - star['y'])
            if self.lake_start_y <= mirror_y < self.lake_end_y:
                ripple = math.sin(self.time * 2 + star['x'] * 0.2) * 1.5
                mirror_x = int(star['x'] + ripple)
                
                # Check if in lake (could use pixel check from BG, but let's just approximate)
                # Actually we can read the pixel from the BG image to see if it's lake color!
                # But that's slow. Let's just draw blindly if it's in bounds.
                if 0 <= mirror_x < self.width:
                     # Make reflection dimmer
                    rr, rg, rb = r//2, g//2, b//2
                    draw.point((mirror_x, mirror_y), fill=(rr, rg, rb))

        # 2. Draw Logs
        for log in self.logs:
            for px, py in log.pixels:
                if 0 <= px < self.width and 0 <= py < self.height:
                    color = log.get_pixel_color(px, py, self.fire_center_x)
                    draw.point((px, py), fill=color)

        # 3. Draw Flames using Lines (Much faster than loops)
        for flame in self.flames:
             base_y = int(flame.base_y)
             height = int(flame.current_height)
             if height <= 0: continue
             
             for dy in range(height):
                y = base_y - dy
                if y < 0: continue
                rel_h = dy / max(1, height)
                
                width_val = flame.get_current_width(rel_h)
                color = flame.get_color_at_height(rel_h)
                
                slice_sway = math.sin(flame.sway_phase * 1.5 + dy * 0.25) * (rel_h * 1.5)
                center_x = flame.x + slice_sway
                
                x1 = center_x - width_val / 2
                x2 = center_x + width_val / 2
                
                # Draw horizontal line for this flame slice
                # Use semi-transparent blending? PIL draw.line doesn't support alpha per se unless RGB
                # We can just draw solid for now, or use a semi-transparent overlay image if we really want glow.
                # Solid is 10x faster and looks fine for pixel art fire.
                draw.line([(x1, y), (x2, y)], fill=color, width=1)

        # 4. Smoke
        for smoke in self.smoke_particles:
            life_ratio = smoke.life / smoke.max_life
            gray = int(40 * life_ratio)
            if gray > 3:
                # Draw small smoke blob
                x, y = int(smoke.x), int(smoke.y)
                draw.point((x,y), fill=(gray, gray, gray+3))
                draw.point((x+1,y), fill=(gray//2, gray//2, gray//2))
                draw.point((x,y-1), fill=(gray//2, gray//2, gray//2))

        # 5. Sparks
        for spark in self.sparks:
            alpha = min(1.0, (spark.life / spark.max_life) * 1.5)
            r = int(255 * alpha)
            g = int(200 * alpha)
            b = int(80 * alpha)
            draw.point((int(spark.x), int(spark.y)), fill=(r,g,b))

        canvas.SetImage(img)