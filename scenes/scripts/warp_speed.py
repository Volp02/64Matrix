from app.core.base_scene import BaseScene
import math
import random
from PIL import Image, ImageDraw

class WarpSpeed(BaseScene):
    """
    Warp speed effect with stars accelerating from center toward camera.
    Features motion blur streaks and tunnel effect.
    Optimized to use PIL for rendering.
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
    
    def _draw_star_with_streak(self, draw, star):
        """Draw a star with motion blur streak using PIL"""
        x = star['x']
        y = star['y']
        size = star['size']
        
        # Calculate streak direction (opposite of movement direction)
        dx = self.center_x - star['x']
        dy = self.center_y - star['y']
        dist_to_center = math.sqrt(dx*dx + dy*dy)
        
        if dist_to_center > 0.1:
            # Normalize direction
            dx /= dist_to_center
            dy /= dist_to_center
            
            # Streak length based on speed/distance
            streak_length = min(15, star['distance'] * 0.3)
            
            # Streak endpoints
            end_x = x - dx * streak_length
            end_y = y - dy * streak_length
            
            # Draw streak (solid color is much faster and looks fine for motion blur)
            # Fading can be simulated by just being dimmer than the star
            streak_color = (25, 50, 100) # Dark blue
            
            # Draw line
            draw.line([(x, y), (end_x, end_y)], fill=streak_color, width=1)
        
        # Draw star (white/yellow)
        r, g, b = star['color']
        
        # Distance fade
        max_dist = 35.0
        brightness = max(0.1, 1.0 - (star['distance'] / max_dist))
        r = int(r * brightness)
        g = int(g * brightness)
        b = int(b * brightness)
        color = (r, g, b)
        
        # Draw star
        radius = size / 2
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)

    def draw(self, canvas):
        # Deep space background (very dark)
        img = Image.new('RGB', (self.width, self.height), (0, 0, 5))
        draw = ImageDraw.Draw(img)
        
        # Draw stars with streaks (sorted by distance for proper layering)
        # Draw farther stars first, then closer ones
        sorted_stars = sorted(self.stars, key=lambda s: s['distance'])
        
        for star in sorted_stars:
            self._draw_star_with_streak(draw, star)
            
        canvas.SetImage(img)
