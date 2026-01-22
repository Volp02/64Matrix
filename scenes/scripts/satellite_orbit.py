from app.core.base_scene import BaseScene
import math
import random


class Satellite(BaseScene):
    """
    Central planet with multiple satellites orbiting in elliptical paths.
    Features fading trails and varying orbit speeds.
    """
    
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        
        # Center of the display (planet position)
        self.center_x = self.width / 2
        self.center_y = self.height / 2
        
        # Planet properties
        self.planet_radius = 8
        self.planet_color = (100, 150, 255)  # Blue planet
        
        # Animation time
        self.time = 0.0
        
        # Create satellites
        self.satellites = []
        self._create_satellites()
        
        # Create star field
        self.stars = []
        self._create_stars()
    
    def _create_satellites(self):
        """Create multiple satellites with different orbits"""
        # Satellite colors
        sat_colors = [
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green
            (255, 255, 100),  # Yellow
            (255, 100, 255),  # Magenta
            (100, 255, 255),  # Cyan
            (255, 150, 50),   # Orange
        ]
        
        # Create 4-6 satellites with varying orbits
        num_satellites = 5
        
        for i in range(num_satellites):
            # Elliptical orbit parameters
            # Semi-major axis (distance from center)
            a = random.uniform(18, 28)
            # Semi-minor axis (ellipticity)
            b = a * random.uniform(0.6, 0.95)  # Make orbits somewhat elliptical
            
            # Orbit angle (where the ellipse is oriented)
            orbit_angle = random.uniform(0, math.pi * 2)
            
            # Starting phase (where satellite starts on orbit)
            phase = random.uniform(0, math.pi * 2)
            
            # Orbital speed (radians per second)
            speed = random.uniform(0.3, 0.8)
            
            # Trail history (stores recent positions)
            trail = []
            
            satellite = {
                'a': a,  # Semi-major axis
                'b': b,  # Semi-minor axis
                'orbit_angle': orbit_angle,  # Rotation of ellipse
                'phase': phase,  # Starting position
                'speed': speed,  # Orbital speed
                'color': sat_colors[i % len(sat_colors)],
                'trail': trail,  # Trail history
                'max_trail_length': 30,  # Max trail points
            }
            
            self.satellites.append(satellite)
    
    def _create_stars(self):
        """Create random stars, some with occasional twinkling"""
        num_stars = 30
        
        for _ in range(num_stars):
            # Random position (avoid center where planet is)
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                # Check if too close to planet center
                dist = math.sqrt((x - self.center_x)**2 + (y - self.center_y)**2)
                if dist > self.planet_radius + 5:  # Keep stars away from planet
                    break
            
            # Base brightness
            brightness = random.uniform(0.4, 0.9)
            
            # Some stars can twinkle (30% chance)
            can_twinkle = random.random() < 0.3
            
            star = {
                'x': x,
                'y': y,
                'base_brightness': brightness,
                'can_twinkle': can_twinkle,
                'twinkle_timer': random.uniform(0, 5.0),  # Random initial timer
                'twinkle_duration': random.uniform(0.3, 0.8),  # How long twinkle lasts
                'twinkle_interval': random.uniform(3.0, 8.0),  # Time between twinkles
            }
            
            self.stars.append(star)
    
    def _get_orbit_position(self, satellite, time):
        """
        Calculate satellite position in elliptical orbit.
        Returns (x, y) position relative to center.
        """
        # Current angle on orbit
        angle = satellite['phase'] + time * satellite['speed']
        
        # Parametric equation for ellipse
        # x = a * cos(t), y = b * sin(t)
        local_x = satellite['a'] * math.cos(angle)
        local_y = satellite['b'] * math.sin(angle)
        
        # Rotate ellipse by orbit_angle
        cos_rot = math.cos(satellite['orbit_angle'])
        sin_rot = math.sin(satellite['orbit_angle'])
        
        x = local_x * cos_rot - local_y * sin_rot
        y = local_x * sin_rot + local_y * cos_rot
        
        return x, y
    
    def update(self, dt):
        self.time += dt
        
        # Update star twinkling
        for star in self.stars:
            if star['can_twinkle']:
                star['twinkle_timer'] += dt
                
                # Check if it's time to twinkle
                if star['twinkle_timer'] >= star['twinkle_interval']:
                    # Start twinkling
                    star['twinkle_timer'] = 0.0
                    star['twinkling'] = True
                    star['twinkle_phase'] = 0.0
                elif star.get('twinkling', False):
                    # Continue twinkling
                    star['twinkle_phase'] += dt
                    if star['twinkle_phase'] >= star['twinkle_duration']:
                        # Stop twinkling
                        star['twinkling'] = False
                        star['twinkle_interval'] = random.uniform(3.0, 8.0)  # New random interval
        
        # Update satellite trails
        for sat in self.satellites:
            x, y = self._get_orbit_position(sat, self.time)
            
            # Add current position to trail
            sat['trail'].append({
                'x': self.center_x + x,
                'y': self.center_y + y,
                'age': 0.0,  # Age in seconds
            })
            
            # Age all trail points
            for trail_point in sat['trail']:
                trail_point['age'] += dt
            
            # Remove old trail points
            sat['trail'] = [p for p in sat['trail'] if p['age'] < 2.0]  # Keep for 2 seconds
            
            # Limit trail length
            if len(sat['trail']) > sat['max_trail_length']:
                sat['trail'] = sat['trail'][-sat['max_trail_length']:]
    
    def _draw_circle(self, canvas, cx, cy, radius, r, g, b):
        """Draw a filled circle"""
        cx_int = int(cx)
        cy_int = int(cy)
        radius_int = int(radius)
        r_sq = radius_int * radius_int
        
        for dy in range(-radius_int, radius_int + 1):
            for dx in range(-radius_int, radius_int + 1):
                if dx*dx + dy*dy <= r_sq:
                    px = cx_int + dx
                    py = cy_int + dy
                    if 0 <= px < self.width and 0 <= py < self.height:
                        canvas.SetPixel(px, py, r, g, b)
    
    def _draw_trail(self, canvas, trail, color, max_age=2.0):
        """Draw fading trail"""
        if len(trail) < 2:
            return
        
        # Draw trail segments
        for i in range(len(trail) - 1):
            p1 = trail[i]
            p2 = trail[i + 1]
            
            # Fade based on age (newer = brighter)
            # Use average age of two points
            avg_age = (p1['age'] + p2['age']) / 2.0
            fade = max(0.0, 1.0 - (avg_age / max_age))
            
            # Apply fade to color
            r = int(color[0] * fade)
            g = int(color[1] * fade)
            b = int(color[2] * fade)
            
            # Draw line segment using Bresenham's algorithm
            x1, y1 = int(p1['x']), int(p1['y'])
            x2, y2 = int(p2['x']), int(p2['y'])
            
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            sx = 1 if x1 < x2 else -1
            sy = 1 if y1 < y2 else -1
            err = dx - dy
            
            x, y = x1, y1
            while True:
                if 0 <= x < self.width and 0 <= y < self.height:
                    canvas.SetPixel(x, y, r, g, b)
                
                if x == x2 and y == y2:
                    break
                
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x += sx
                if e2 < dx:
                    err += dx
                    y += sy
    
    def draw(self, canvas):
        # Dark space background
        canvas.Fill(5, 5, 10)
        
        # Draw stars
        for star in self.stars:
            brightness = star['base_brightness']
            
            # Apply subtle twinkling if active
            if star.get('twinkling', False):
                # Subtle twinkle: fade in and out smoothly
                twinkle_progress = star['twinkle_phase'] / star['twinkle_duration']
                # Smooth sine wave for gentle fade
                twinkle_factor = (math.sin(twinkle_progress * math.pi) + 1.0) / 2.0
                # Subtle effect: only vary brightness by 20-30%
                brightness = star['base_brightness'] * (0.7 + twinkle_factor * 0.3)
            
            # Convert brightness to color (white/blue-white stars)
            star_value = int(200 * brightness)
            canvas.SetPixel(star['x'], star['y'], star_value, star_value, int(star_value * 1.1))
        
        # Draw satellite trails first (so they appear behind satellites)
        for sat in self.satellites:
            if len(sat['trail']) > 1:
                self._draw_trail(canvas, sat['trail'], sat['color'])
        
        # Draw central planet
        self._draw_circle(
            canvas,
            self.center_x,
            self.center_y,
            self.planet_radius,
            *self.planet_color
        )
        
        # Draw planet highlight (small bright spot)
        highlight_r = int(self.planet_color[0] * 1.3)
        highlight_g = int(self.planet_color[1] * 1.3)
        highlight_b = int(self.planet_color[2] * 1.3)
        highlight_r = min(255, highlight_r)
        highlight_g = min(255, highlight_g)
        highlight_b = min(255, highlight_b)
        
        self._draw_circle(
            canvas,
            self.center_x - 2,
            self.center_y - 2,
            2,
            highlight_r, highlight_g, highlight_b
        )
        
        # Draw satellites
        for sat in self.satellites:
            x, y = self._get_orbit_position(sat, self.time)
            sat_x = self.center_x + x
            sat_y = self.center_y + y
            
            # Draw satellite (small circle)
            self._draw_circle(
                canvas,
                sat_x,
                sat_y,
                2,
                *sat['color']
            )
            
            # Draw bright center dot
            self._draw_circle(
                canvas,
                sat_x,
                sat_y,
                1,
                255, 255, 255  # White center
            )
