from app.core.base_scene import BaseScene
import math
import random

class WaveInterference(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.time = 0.0
        
        # Wave Sources
        # Each source: x, y, frequency (k), phase speed (w)
        # We make them move slowly to change the pattern
        self.sources = []
        num_sources = 3
        for _ in range(num_sources):
            self.sources.append({
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height),
                'vx': random.uniform(-10, 10),
                'vy': random.uniform(-10, 10),
                'freq': random.uniform(0.3, 0.6), # Spatial frequency (tightness of ripples)
                'speed': random.uniform(4.0, 8.0) # Temporal speed (how fast ripples move out)
            })

    def get_palette(self):
        try:
            palette_mgr = getattr(self.state_manager, '_palette_manager', None)
            if palette_mgr:
                return self.state_manager.get_palette_colors(palette_mgr)
        except:
            pass
        return None

    def update(self, dt):
        self.time += dt
        
        # Move sources
        for s in self.sources:
            s['x'] += s['vx'] * dt
            s['y'] += s['vy'] * dt
            
            # Bounce off walls
            if s['x'] < 0:
                s['x'] = 0
                s['vx'] *= -1
            elif s['x'] > self.width:
                s['x'] = self.width
                s['vx'] *= -1
                
            if s['y'] < 0:
                s['y'] = 0
                s['vy'] *= -1
            elif s['y'] > self.height:
                s['y'] = self.height
                s['vy'] *= -1

    def draw(self, canvas):
        w = self.width
        h = self.height
        t = self.time
        sources = self.sources
        
        # Fetch palette
        colors = self.get_palette()
        
        for y in range(h):
            for x in range(w):
                amplitude = 0.0
                
                # Sum waves from all sources
                for s in sources:
                    dx = x - s['x']
                    dy = y - s['y']
                    # Sqrt is somewhat expensive, but needed for circular ripples
                    dist = math.sqrt(dx*dx + dy*dy)
                    amplitude += math.sin(dist * s['freq'] - t * s['speed'])
                
                # Normalize amplitude (-N to N) -> (0 to 1)
                norm_amp = (amplitude / len(sources) + 1.0) / 2.0
                norm_amp = max(0.0, min(1.0, norm_amp))
                
                # Color Mapping
                r, g, b = 0, 0, 0
                
                if colors and len(colors) >= 2:
                    # Interpolate through palette
                    # Map 0..1 to 0..(len-1)
                    idx = norm_amp * (len(colors) - 1)
                    i = int(idx)
                    f = idx - i
                    
                    c1 = colors[i]
                    c2 = colors[min(i + 1, len(colors) - 1)]
                    
                    r = int(c1[0] + (c2[0] - c1[0]) * f)
                    g = int(c1[1] + (c2[1] - c1[1]) * f)
                    b = int(c1[2] + (c2[2] - c1[2]) * f)
                else:
                    # Fallback Cyan/Blue scheme
                    intensity = int(norm_amp * 255)
                    r = 0
                    g = intensity
                    b = max(100, intensity)
                    
                    if norm_amp > 0.8:
                        extra = int((norm_amp - 0.8) * 5 * 255)
                        r = extra
                        g = 255
                        b = 255
                
                canvas.SetPixel(x, y, r, g, b)
