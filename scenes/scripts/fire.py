from app.core.base_scene import BaseScene
import random
import math


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
        # Flames NEVER die
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
        
        # Calculate pixels
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
        self.mountains = self._generate_mountains()
        self.lake_pixels = self._generate_lake_shape()
        
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
        
        # Glow buffer for flame rendering
        self.glow_buffer = {}
    
    def _generate_stars(self):
        """Generate random star positions in the sky"""
        stars = []
        for _ in range(35):  # Number of stars
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.horizon_y - 5)
            brightness = random.uniform(0.4, 1.0)
            twinkle_speed = random.uniform(1.5, 4.0)
            twinkle_phase = random.uniform(0, math.pi * 2)
            stars.append({
                'x': x,
                'y': y,
                'brightness': brightness,
                'twinkle_speed': twinkle_speed,
                'twinkle_phase': twinkle_phase
            })
        return stars
    
    def _generate_mountains(self):
        """Generate mountain silhouettes with snow caps"""
        mountains = []
        
        # Mountain positions: (center_x, height, width_factor)
        mountain_data = [
            (5, 14, 1.2),
            (15, 20, 1.0),
            (25, 12, 0.9),
            (42, 15, 1.1),
            (52, 22, 1.0),
            (60, 11, 0.8),
        ]
        
        for center_x, height, width_factor in mountain_data:
            mountain_pixels = []  # (x, y, is_snow)
            
            # Create mountain shape (triangle)
            for y_offset in range(height):
                # Width increases toward bottom
                rel_height = y_offset / height
                width = int((1 + rel_height * height * 0.4) * width_factor)
                mountain_y = self.horizon_y - height + y_offset
                
                # Snow line - top 25% of mountain has snow
                is_snow = rel_height < 0.25
                
                for dx in range(-width, width + 1):
                    mountain_x = center_x + dx
                    if 0 <= mountain_x < self.width and 0 <= mountain_y < self.height:
                        # Add some jaggedness to snow line
                        snow_threshold = 0.25 + random.uniform(-0.05, 0.05)
                        pixel_is_snow = rel_height < snow_threshold
                        mountain_pixels.append((mountain_x, mountain_y, pixel_is_snow))
            
            mountains.append(mountain_pixels)
        
        return mountains
    
    def _generate_lake_shape(self):
        """Generate a natural curved lake shape"""
        lake_pixels = set()
        
        # Lake is an irregular oval/blob shape
        lake_center_x = self.width // 2
        lake_center_y = (self.lake_start_y + self.lake_end_y) // 2
        lake_width = 22  # Half-width
        lake_height = (self.lake_end_y - self.lake_start_y) // 2
        
        for y in range(self.lake_start_y, self.lake_end_y):
            for x in range(self.width):
                # Ellipse equation with some noise for natural shape
                dx = (x - lake_center_x) / lake_width
                dy = (y - lake_center_y) / max(1, lake_height)
                
                # Add shoreline variation
                noise = math.sin(x * 0.3) * 0.15 + math.sin(x * 0.7) * 0.1
                
                dist = dx * dx + dy * dy + noise
                
                if dist < 1.0:
                    lake_pixels.add((x, y))
        
        return lake_pixels
        
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
    
    def enter(self, state_manager):
        """Create all flames - they persist forever"""
        # Clear any existing flames
        self.flames = []
        # Create a good number of persistent flames
        for _ in range(50):
            self._spawn_flame()
    
    def _spawn_flame(self):
        """Spawn a new flame from a random spawn point"""
        if not self.all_spawn_points:
            return
            
        # Weight spawn points toward center
        weights = []
        for x, y in self.all_spawn_points:
            dist = abs(x - self.fire_center_x)
            weight = max(0.3, 1.0 - dist / 25.0)
            weights.append(weight)
        
        # Weighted random selection
        total = sum(weights)
        r = random.uniform(0, total)
        cumulative = 0
        chosen = self.all_spawn_points[0]
        for i, (point, w) in enumerate(zip(self.all_spawn_points, weights)):
            cumulative += w
            if r <= cumulative:
                chosen = point
                break
        
        x, y = chosen
        # Add slight randomness to spawn position
        x += random.uniform(-1.5, 1.5)
        y += random.uniform(-1, 1)
        
        # Center flames are more intense
        dist = abs(x - self.fire_center_x)
        intensity = max(0.5, 1.0 - dist / 30.0)
        intensity *= random.uniform(0.8, 1.2)
        
        self.flames.append(Flame(x, y, intensity))
    
    def _spawn_spark(self):
        """Spawn a spark from within a flame"""
        if self.flames:
            flame = random.choice(self.flames)
            # Spawn from somewhere along the flame's height
            spark_y = flame.base_y - random.uniform(3, flame.current_height * 0.7)
            self.sparks.append(Spark(flame.x, spark_y))
    
    def _spawn_smoke(self):
        """Spawn smoke above flames"""
        if self.flames:
            # Pick a random flame and spawn smoke above it
            flame = random.choice(self.flames)
            smoke_y = flame.base_y - flame.current_height - 2
            self.smoke_particles.append(Smoke(flame.x + random.uniform(-3, 3), smoke_y))
    
    def update(self, dt):
        self.time += dt
        
        # Update all persistent flames (they never die)
        for flame in self.flames:
            flame.update(dt)
        
        # Ensure we always have enough flames
        if len(self.flames) < 50:
            self._spawn_flame()
        
        # Spawn sparks
        self.spark_timer += dt
        if self.spark_timer > 0.1:
            self.spark_timer = 0
            if random.random() < 0.4:
                self._spawn_spark()
        
        # Spawn smoke - more frequently for atmosphere
        self.smoke_timer += dt
        if self.smoke_timer > 0.08:
            self.smoke_timer = 0
            if random.random() < 0.6:
                self._spawn_smoke()
        
        # Update sparks (these can die)
        for spark in self.sparks:
            spark.update(dt)
        self.sparks = [s for s in self.sparks if s.is_alive()]
        
        # Update smoke (these can die)
        for smoke in self.smoke_particles:
            smoke.update(dt)
        self.smoke_particles = [s for s in self.smoke_particles if s.is_alive()]
        
        # Update wood embers
        for log in self.logs:
            log.update_embers(dt)
        
        # Update star twinkle
        for star in self.stars:
            star['twinkle_phase'] += star['twinkle_speed'] * dt
        
        # Limit sparks and smoke
        if len(self.sparks) > 20:
            self.sparks = self.sparks[-20:]
        if len(self.smoke_particles) > 40:  # More smoke allowed
            self.smoke_particles = self.smoke_particles[-40:]
    
    def _draw_flame(self, canvas, flame):
        """Draw a single persistent flame with flickering shape"""
        base_y = int(flame.base_y)
        height = int(flame.current_height)
        
        if height <= 0:
            return
        
        # Draw flame from base to tip
        for dy in range(height):
            y = base_y - dy
            if y < 0 or y >= self.height:
                continue
            
            # Relative height (0 at base, 1 at tip)
            rel_h = dy / max(1, height)
            
            # Get width at this height (includes flickering)
            width = flame.get_current_width(rel_h)
            
            # Get color for this height
            color = flame.get_color_at_height(rel_h)
            
            # Horizontal position - flame.x already has base sway
            # Add additional per-slice waviness for organic look
            slice_sway = math.sin(flame.sway_phase * 1.5 + dy * 0.25) * (rel_h * 1.5)
            center_x = flame.x + slice_sway
            
            # Draw horizontal slice of flame
            half_width = width / 2
            for dx_f in range(-int(half_width + 1), int(half_width + 2)):
                x = int(center_x + dx_f)
                if 0 <= x < self.width:
                    # Fade at edges - gentler fade for fuller flames
                    edge_dist = abs(dx_f) / max(0.5, half_width)
                    if edge_dist <= 1.2:
                        edge_fade = max(0.35, 1.0 - edge_dist * 0.35)
                        r = int(color[0] * edge_fade)
                        g = int(color[1] * edge_fade)
                        b = int(color[2] * edge_fade)
                        
                        # Additive blending with existing glow
                        key = (x, y)
                        if key in self.glow_buffer:
                            old = self.glow_buffer[key]
                            r = min(255, old[0] + r)
                            g = min(255, old[1] + g)
                            b = min(255, old[2] + b)
                        self.glow_buffer[key] = (r, g, b)
    
    def draw(self, canvas):
        # Clear glow buffer
        self.glow_buffer = {}
        
        # === BACKGROUND: Night Sky ===
        # Dark blue gradient sky
        for y in range(self.horizon_y):
            # Gradient from darker at top to slightly lighter near horizon
            gradient = y / self.horizon_y
            sky_r = int(5 + gradient * 8)
            sky_g = int(8 + gradient * 12)
            sky_b = int(25 + gradient * 20)
            for x in range(self.width):
                canvas.SetPixel(x, y, sky_r, sky_g, sky_b)
        
        # === STARS in sky ===
        for star in self.stars:
            x, y = star['x'], star['y']
            # Twinkle effect
            twinkle = (math.sin(star['twinkle_phase']) * 0.3 + 0.7)
            brightness = star['brightness'] * twinkle
            
            # Star color (slight yellow-white)
            sr = int(255 * brightness)
            sg = int(250 * brightness)
            sb = int(220 * brightness)
            
            if 0 <= x < self.width and 0 <= y < self.height:
                canvas.SetPixel(x, y, sr, sg, sb)
        
        # === GROUND AND LAKE AREA ===
        for y in range(self.lake_start_y, self.height):
            for x in range(self.width):
                if (x, y) in self.lake_pixels:
                    # Lake water - darker toward edges/bottom
                    depth = (y - self.lake_start_y) / max(1, self.lake_end_y - self.lake_start_y)
                    lake_r = int(4 + (1 - depth) * 6)
                    lake_g = int(6 + (1 - depth) * 10)
                    lake_b = int(20 + (1 - depth) * 18)
                    canvas.SetPixel(x, y, lake_r, lake_g, lake_b)
                else:
                    # Ground/shore - dark earth tones
                    canvas.SetPixel(x, y, 10, 8, 5)
        
        # Star reflections in lake (only where lake exists)
        for star in self.stars:
            # Mirror y position into lake
            mirror_y = self.lake_start_y + (self.horizon_y - star['y'])
            
            if self.lake_start_y <= mirror_y < self.lake_end_y:
                # Ripple effect - slight horizontal wobble
                ripple = math.sin(self.time * 2 + star['x'] * 0.2) * 1.5
                mirror_x = int(star['x'] + ripple)
                
                # Only draw reflection if it's in the lake
                if (mirror_x, int(mirror_y)) in self.lake_pixels:
                    # Dimmer reflection
                    twinkle = (math.sin(star['twinkle_phase'] + 1) * 0.2 + 0.5)
                    brightness = star['brightness'] * twinkle * 0.4
                    
                    sr = int(200 * brightness)
                    sg = int(200 * brightness)
                    sb = int(180 * brightness)
                    
                    if 0 <= mirror_x < self.width:
                        canvas.SetPixel(mirror_x, int(mirror_y), sr, sg, sb)
        
        # === MOUNTAIN SILHOUETTES WITH SNOW CAPS ===
        for mountain_pixels in self.mountains:
            for mx, my, is_snow in mountain_pixels:
                if 0 <= mx < self.width and 0 <= my < self.height:
                    if is_snow:
                        # Gray snow (dark because it's night)
                        canvas.SetPixel(mx, my, 45, 50, 55)
                    else:
                        # Dark mountain rock
                        canvas.SetPixel(mx, my, 5, 5, 8)
        
        # === SMOKE (semi-transparent over background) ===
        for smoke in self.smoke_particles:
            sx, sy = int(smoke.x), int(smoke.y)
            life_ratio = smoke.life / smoke.max_life
            gray = int(40 * life_ratio)
            
            if 0 <= sx < self.width and 0 <= sy < self.height and gray > 3:
                canvas.SetPixel(sx, sy, gray, gray, gray + 3)
                # Expand smoke a bit
                for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = sx + ddx, sy + ddy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        canvas.SetPixel(nx, ny, gray // 2, gray // 2, gray // 2 + 2)
        
        # === WOOD LOGS ===
        for log in self.logs:
            for px, py in log.pixels:
                if 0 <= px < self.width and 0 <= py < self.height:
                    r, g, b = log.get_pixel_color(px, py, self.fire_center_x)
                    canvas.SetPixel(px, py, r, g, b)
        
        # === FLAMES ===
        for flame in self.flames:
            self._draw_flame(canvas, flame)
        
        # Draw glow buffer (flames)
        for (x, y), (r, g, b) in self.glow_buffer.items():
            if 0 <= x < self.width and 0 <= y < self.height:
                canvas.SetPixel(x, y, r, g, b)
        
        # === SPARKS on top ===
        for spark in self.sparks:
            sx, sy = int(spark.x), int(spark.y)
            if 0 <= sx < self.width and 0 <= sy < self.height:
                alpha = min(1.0, (spark.life / spark.max_life) * 1.5)
                r = int(255 * alpha)
                g = int(200 * alpha)
                b = int(80 * alpha)
                canvas.SetPixel(sx, sy, r, g, b)