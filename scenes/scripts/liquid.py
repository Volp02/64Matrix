from app.core.base_scene import BaseScene
import random
import math

class LiquidParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        
class Liquid(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.particles = []
        self.num_particles = 40
        self.gravity = 25.0
        self.damp = 0.95
        self.time_tracker = 0.0
        
        self.spawn_liquid()

    def spawn_liquid(self):
        cx, cy = self.width / 2, self.height / 2
        for _ in range(self.num_particles):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(0, 10)
            self.particles.append(LiquidParticle(cx + math.cos(angle)*dist, cy + math.sin(angle)*dist))

    def update(self, dt):
        self.time_tracker += dt
        
        # 0. Dynamic Environment (Sloshing)
        # Gravity vector rotates slightly to simulate tilting container
        tilt_amount = math.sin(self.time_tracker * 1.5) * 15.0  # +/- 15 accel sideways
        gx = tilt_amount
        gy = self.gravity + math.cos(self.time_tracker * 2.3) * 5.0  # Pulse vertical gravity
        
        # Random "Agitation" / Shake every few seconds
        shake = False
        if random.random() < 0.005:  # ~Once every 3-4 seconds at 60fps
            shake = True
            shake_x = random.uniform(-100, 100)
            shake_y = random.uniform(-150, -50) # Kick up
        
        # 1. Update Physics
        for p in self.particles:
            # Apply Dynamic Gravity
            p.vx += gx * dt
            p.vy += gy * dt
            
            # Apply Shake
            if shake:
                p.vx += shake_x
                p.vy += shake_y
            
            # Predict position
            p.x += p.vx * dt
            p.y += p.vy * dt
            
            # Floor constraint
            if p.y > self.height - 2:
                p.y = self.height - 2
                p.vy *= -0.6  # More bounce
                p.vx *= 0.9
                
            # Wall constraints
            if p.x < 1:
                p.x = 1
                p.vx *= -0.6
                p.vy *= 0.95 # Wall friction
            elif p.x > self.width - 2:
                p.x = self.width - 2
                p.vx *= -0.6
                p.vy *= 0.95
                
            # Ceiling constraint
            if p.y < 0:
                p.y = 0
                p.vy *= -0.6

        # 2. Particle Repulsion (The "Fluid" part)
        # O(N^2) but with 40 particles ~1600 checks, fine for Python
        for i in range(len(self.particles)):
            p1 = self.particles[i]
            for j in range(i + 1, len(self.particles)):
                p2 = self.particles[j]
                
                dx = p1.x - p2.x
                dy = p1.y - p2.y
                dist_sq = dx*dx + dy*dy
                
                # If too close, push apart
                min_dist = 3.0 # Liquid "radius"
                if dist_sq < min_dist * min_dist and dist_sq > 0.001:
                    dist = math.sqrt(dist_sq)
                    overlap = min_dist - dist
                    
                    # Force direction
                    nx = dx / dist
                    ny = dy / dist
                    
                    # Move apart (position based dynamics is more stable than force for this)
                    move = overlap * 0.5
                    factor = 0.5 # Relax factor
                    
                    p1.x += nx * move * factor
                    p1.y += ny * move * factor
                    p2.x -= nx * move * factor
                    p2.y -= ny * move * factor
                    
                    # Average velocities slightly (Viscosity)
                    avg_vx = (p1.vx + p2.vx) * 0.5
                    avg_vy = (p1.vy + p2.vy) * 0.5
                    visc = 0.1
                    p1.vx = p1.vx * (1-visc) + avg_vx * visc
                    p2.vx = p2.vx * (1-visc) + avg_vy * visc

    def draw(self, canvas):
        # "Splat" the particles into a density grid
        # 0.0 to 1.0+
        # We only need to clear the screen, splatting will determine color
        canvas.Clear()
        
        # We can draw directly to canvas by summing influences?
        # No, we need a grid to sum density first, THEN map to color.
        
        # Optimization: Only Splat into a small grid or dictionary? 
        # 64x64 is small. Array lookup is fast.
        
        density = [[0.0] * self.width for _ in range(self.height)]
        
        # Splat kernel (approx 3x3 gaussian)
        radius = 4
        
        for p in self.particles:
            px_int = int(p.x)
            py_int = int(p.y)
            
            # Bounding box for splat
            min_x = max(0, px_int - radius)
            max_x = min(self.width, px_int + radius + 1)
            min_y = max(0, py_int - radius)
            max_y = min(self.height, py_int + radius + 1)
            
            for y in range(min_y, max_y):
                for x in range(min_x, max_x):
                    dx = x - p.x
                    dy = y - p.y
                    d2 = dx*dx + dy*dy
                    if d2 < radius*radius:
                        # Influence function: (1 - r^2/R^2)^2 (Metaball falloff)
                        inf = (1.0 - d2/(radius*radius))
                        density[y][x] += inf * inf * 1.5 # Boost density

        # Render density to colors
        for y in range(self.height):
            for x in range(self.width):
                d = density[y][x]
                if d > 0.1: # Threshold to draw
                    # Liquid coloring: Blue/Cyan gradient based on density
                    # Threshold for "surface"
                    
                    # Clamping density for color mapping
                    val = min(1.0, d / 2.0)
                    
                    # Deep blue center, Cyan edge
                    # If dense (center): Darker Blue
                    # If light (edge): Brighter Cyan/White
                    
                    # Let's try:
                    # Edge (d ~ 0.2): (0, 255, 255)
                    # Center (d > 1.0): (0, 0, 200)
                    
                    if d < 0.3:
                        # Outer glow/surface
                        r, g, b = 0, 200, 255
                        alpha = d / 0.3
                        r = int(r * alpha)
                        g = int(g * alpha)
                        b = int(b * alpha)
                    else:
                        # Inner body
                        # Lerp from Cyan (0,255,255) to Blue (0,0,255)
                        t = min(1.0, (d - 0.3) / 1.5)
                        r = 0
                        g = int(255 * (1.0 - t))
                        b = 255
                    
                    canvas.SetPixel(x, y, r, g, b)
