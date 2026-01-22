from app.core.base_scene import BaseScene
import math
import random


class Nebula(BaseScene):
    """
    Ethereal nebula with colorful, wispy clouds of gas.
    Features slow drift, morphing, and soft blended edges with depth layers.
    """
    
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        
        # Animation time
        self.time = 0.0
        
        # Nebula layers - each with different color and movement
        self.layers = []
        
        # Create multiple cloud layers for depth
        self._create_layers()
        
        # Star field for background
        self.stars = []
        for _ in range(40):
            self.stars.append({
                'x': random.randint(0, self.width - 1),
                'y': random.randint(0, self.height - 1),
                'brightness': random.uniform(0.3, 1.0),
                'twinkle_speed': random.uniform(1.0, 3.0),
                'twinkle_phase': random.uniform(0, math.pi * 2),
            })
    
    def _create_layers(self):
        """Create multiple nebula cloud layers with different colors and properties"""
        # Deep purple layer (background)
        self.layers.append({
            'color': (80, 20, 120),  # Deep purple
            'offset_x': 0.0,
            'offset_y': 0.0,
            'drift_x': 0.02,
            'drift_y': 0.015,
            'scale': 0.08,
            'intensity': 0.6,
            'noise_phase': random.uniform(0, math.pi * 2),
        })
        
        # Blue layer
        self.layers.append({
            'color': (30, 60, 150),  # Deep blue
            'offset_x': 10.0,
            'offset_y': 15.0,
            'drift_x': -0.025,
            'drift_y': 0.02,
            'scale': 0.1,
            'intensity': 0.7,
            'noise_phase': random.uniform(0, math.pi * 2),
        })
        
        # Pink layer
        self.layers.append({
            'color': (180, 50, 120),  # Pink
            'offset_x': -15.0,
            'offset_y': 10.0,
            'drift_x': 0.018,
            'drift_y': -0.022,
            'scale': 0.12,
            'intensity': 0.65,
            'noise_phase': random.uniform(0, math.pi * 2),
        })
        
        # Orange/red layer (foreground)
        self.layers.append({
            'color': (200, 80, 40),  # Orange-red
            'offset_x': 20.0,
            'offset_y': -10.0,
            'drift_x': -0.02,
            'drift_y': -0.018,
            'scale': 0.09,
            'intensity': 0.55,
            'noise_phase': random.uniform(0, math.pi * 2),
        })
        
        # Cyan accent layer
        self.layers.append({
            'color': (40, 150, 180),  # Cyan
            'offset_x': -10.0,
            'offset_y': -15.0,
            'drift_x': 0.015,
            'drift_y': 0.025,
            'scale': 0.11,
            'intensity': 0.5,
            'noise_phase': random.uniform(0, math.pi * 2),
        })
    
    def _noise(self, x, y, time, scale, phase):
        """
        Simple 2D noise function using multiple sine waves.
        Creates organic, cloud-like patterns.
        """
        # Combine multiple sine waves for organic noise
        n1 = math.sin(x * scale + time * 0.1 + phase) * 0.5
        n2 = math.sin(y * scale * 0.7 + time * 0.08 + phase * 1.3) * 0.3
        n3 = math.sin((x + y) * scale * 0.5 + time * 0.12 + phase * 0.7) * 0.2
        
        # Add some turbulence
        n4 = math.sin((x * 1.3 - y * 0.8) * scale * 0.4 + time * 0.15 + phase * 2.1) * 0.15
        
        return (n1 + n2 + n3 + n4) / 1.15  # Normalize to roughly -1 to 1
    
    def _get_cloud_density(self, x, y, layer, time):
        """Get cloud density at a point for a specific layer"""
        # Apply layer offset and drift
        layer_x = x + layer['offset_x'] + time * layer['drift_x'] * 50
        layer_y = y + layer['offset_y'] + time * layer['drift_y'] * 50
        
        # Get noise value
        noise_val = self._noise(layer_x, layer_y, time, layer['scale'], layer['noise_phase'])
        
        # Convert noise to density (0 to 1)
        # Use smoothstep-like function for softer edges
        density = (noise_val + 1.0) / 2.0  # 0 to 1
        
        # Apply threshold and smooth falloff for wispy edges
        threshold = 0.3
        if density < threshold:
            return 0.0
        
        # Smooth falloff from threshold to 1.0
        t = (density - threshold) / (1.0 - threshold)
        # Smooth curve for soft edges
        t = t * t * (3.0 - 2.0 * t)  # Smoothstep
        
        return t * layer['intensity']
    
    def update(self, dt):
        self.time += dt
        
        # Update star twinkling (handled in draw)
        pass
    
    def draw(self, canvas):
        # Deep space background
        canvas.Fill(5, 5, 15)
        
        # Draw twinkling stars
        for star in self.stars:
            twinkle = (math.sin(self.time * star['twinkle_speed'] + star['twinkle_phase']) + 1.0) / 2.0
            brightness = star['brightness'] * (0.5 + twinkle * 0.5)
            
            star_r = int(200 * brightness)
            star_g = int(200 * brightness)
            star_b = int(220 * brightness)
            
            canvas.SetPixel(star['x'], star['y'], star_r, star_g, star_b)
        
        # Build nebula by blending layers
        # Use a buffer to accumulate colors with additive blending
        nebula_buffer = {}
        
        for y in range(self.height):
            for x in range(self.width):
                # Accumulate colors from all layers
                r, g, b = 0, 0, 0
                
                for layer in self.layers:
                    density = self._get_cloud_density(x, y, layer, self.time)
                    
                    if density > 0.01:  # Only process if visible
                        layer_r, layer_g, layer_b = layer['color']
                        
                        # Additive blending for ethereal glow
                        r += int(layer_r * density)
                        g += int(layer_g * density)
                        b += int(layer_b * density)
                
                # Clamp and store
                r = min(255, r)
                g = min(255, g)
                b = min(255, b)
                
                if r > 10 or g > 10 or b > 10:  # Only store if visible
                    nebula_buffer[(x, y)] = (r, g, b)
        
        # Draw nebula with soft blending over stars
        for (x, y), (r, g, b) in nebula_buffer.items():
            # Get star color if present
            star_r, star_g, star_b = 5, 5, 15  # Background color
            
            # Check if there's a star here
            for star in self.stars:
                if star['x'] == x and star['y'] == y:
                    twinkle = (math.sin(self.time * star['twinkle_speed'] + star['twinkle_phase']) + 1.0) / 2.0
                    brightness = star['brightness'] * (0.5 + twinkle * 0.5)
                    star_r = int(200 * brightness)
                    star_g = int(200 * brightness)
                    star_b = int(220 * brightness)
                    break
            
            # Blend nebula with star/background
            # Nebula has some transparency for ethereal effect
            nebula_alpha = 0.85
            out_r = int(r * nebula_alpha + star_r * (1.0 - nebula_alpha))
            out_g = int(g * nebula_alpha + star_g * (1.0 - nebula_alpha))
            out_b = int(b * nebula_alpha + star_b * (1.0 - nebula_alpha))
            
            canvas.SetPixel(x, y, out_r, out_g, out_b)
