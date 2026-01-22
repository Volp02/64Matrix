from app.core.base_scene import BaseScene
import math
import random


class WarpSpeed(BaseScene):
    """
    Warp speed effect with stars accelerating from center toward camera.
    Features motion blur streaks and tunnel effect.
    """
    
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        
        # Center of the display
        self.center_x = self.width / 2
        self.center_y = self.height / 2
        
        # Star particles
        self.stars = []
        
        # Spawn parameters
        self.spawn_timer = 0.0
        self.spawn_interval = 0.05  # Spawn new star every 0.05 seconds
        
        # Animation time
        self.time = 0.0
        
        # Speed multiplier (increases over time for acceleration effect)
        self.base_speed = 20.0  # Base speed in pixels per second
        
        # Initialize with some stars
        for _ in range(30):
            self._spawn_star()
    
    def _spawn_star(self):
        """Spawn a new star at the center"""
        # Random angle from center
        angle = random.uniform(0, math.pi * 2)
        
        # Random distance from center (slight offset to avoid all starting at exact center)
        start_dist = random.uniform(0.5, 2.0)
        
        # Random speed variation
        speed_mult = random.uniform(0.8, 1.2)
        
        # Star color (white to yellow)
        color_choice = random.random()
        if color_choice < 0.7:
            # White stars
            color = (255, 255, 255)
        elif color_choice < 0.9:
            # Yellow-white stars
            color = (255, 255, 200)
        else:
            # Warm yellow stars
            color = (255, 240, 150)
        
        star = {
            'x': self.center_x + math.cos(angle) * start_dist,
            'y': self.center_y + math.sin(angle) * start_dist,
            'angle': angle,
            'distance': start_dist,
            'speed': self.base_speed * speed_mult,
            'color': color,
            'size': 0.5,  # Starting size (very small)
        }
        
        self.stars.append(star)
    
    def update(self, dt):
        self.time += dt
        
        # Spawn new stars
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self._spawn_star()
        
        # Update stars
        stars_to_remove = []
        
        for star in self.stars:
            # Accelerate star outward
            # Speed increases with distance (creates acceleration effect)
            speed_factor = 1.0 + star['distance'] * 0.1
            star['distance'] += star['speed'] * speed_factor * dt
            
            # Update position
            star['x'] = self.center_x + math.cos(star['angle']) * star['distance']
            star['y'] = self.center_y + math.sin(star['angle']) * star['distance']
            
            # Star gets larger as it moves away (perspective effect)
            # Cap size at 3 pixels max
            star['size'] = min(3.0, 0.5 + star['distance'] * 0.08)
            
            # Remove stars that have moved off screen
            margin = 10
            if (star['x'] < -margin or star['x'] > self.width + margin or
                star['y'] < -margin or star['y'] > self.height + margin):
                stars_to_remove.append(star)
        
        # Remove off-screen stars
        for star in stars_to_remove:
            self.stars.remove(star)
    
    def _draw_star_with_streak(self, canvas, star):
        """Draw a star with motion blur streak"""
        x = int(star['x'])
        y = int(star['y'])
        size = int(star['size'])
        
        # Calculate streak direction (opposite of movement direction)
        # Streak points back toward center
        dx = self.center_x - star['x']
        dy = self.center_y - star['y']
        dist_to_center = math.sqrt(dx*dx + dy*dy)
        
        if dist_to_center > 0.1:
            # Normalize direction
            dx /= dist_to_center
            dy /= dist_to_center
            
            # Streak length based on speed/distance
            streak_length = min(15, star['distance'] * 0.3)
            
            # Draw streak (motion blur) - blue/cyan
            streak_start_x = x
            streak_start_y = y
            streak_end_x = int(x - dx * streak_length)
            streak_end_y = int(y - dy * streak_length)
            
            # Draw streak line with fading intensity (bright at star, dark towards center)
            self._draw_fading_line(
                canvas,
                streak_start_x, streak_start_y,  # Start at star (bright)
                streak_end_x, streak_end_y,      # End towards center (dark)
                (50, 100, 200),  # Blue streak color
                0.4  # Streak opacity
            )
        
        # Draw star (white/yellow)
        r, g, b = star['color']
        
        # Brightness based on distance (closer to center = brighter, fades as it moves away)
        # Start bright at center (distance ~0), fade to ~10% at edges
        # Use inverse relationship: brightness decreases with distance
        max_dist = 35.0  # Approximate max distance before off-screen
        brightness = max(0.1, 1.0 - (star['distance'] / max_dist))
        r = int(r * brightness)
        g = int(g * brightness)
        b = int(b * brightness)
        
        # Draw star as small circle or point
        if size <= 1:
            # Single pixel
            if 0 <= x < self.width and 0 <= y < self.height:
                canvas.SetPixel(x, y, r, g, b)
        else:
            # Small circle
            size_int = int(size)
            for dy in range(-size_int, size_int + 1):
                for dx in range(-size_int, size_int + 1):
                    if dx*dx + dy*dy <= size_int * size_int:
                        px = x + dx
                        py = y + dy
                        if 0 <= px < self.width and 0 <= py < self.height:
                            canvas.SetPixel(px, py, r, g, b)
    
    def _draw_fading_line(self, canvas, x1, y1, x2, y2, color, base_alpha):
        """Draw a line with fading intensity from start to end"""
        # Bresenham's line algorithm with fading
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        total_steps = max(dx, dy)
        step = 0
        
        r_base, g_base, b_base = color
        
        while True:
            if 0 <= x < self.width and 0 <= y < self.height:
                # Fade from start (brighter) to end (darker towards center)
                fade = 1.0 - (step / max(1, total_steps))  # Reverse: 1.0 at start, 0.0 at end
                alpha = base_alpha * (0.1 + fade * 0.9)  # Fade from 100% to 10% of base_alpha
                
                r = int(r_base * alpha)
                g = int(g_base * alpha)
                b = int(b_base * alpha)
                
                canvas.SetPixel(x, y, r, g, b)
            
            if x == x2 and y == y2:
                break
            
            step += 1
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def draw(self, canvas):
        # Deep space background (very dark)
        canvas.Fill(0, 0, 5)
        
        # Draw stars with streaks (sorted by distance for proper layering)
        # Draw farther stars first, then closer ones
        sorted_stars = sorted(self.stars, key=lambda s: s['distance'])
        
        for star in sorted_stars:
            self._draw_star_with_streak(canvas, star)
