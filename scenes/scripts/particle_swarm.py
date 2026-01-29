from app.core.base_scene import BaseScene
import random
import math

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.color = color
        self.mass = random.uniform(0.5, 1.5)
        self.radius = 1
        
    def update(self, dt, particles, width, height, attraction_strength, repulsion_strength, damping):
        """Update particle physics with forces from other particles"""
        fx = 0.0  # Force in x direction
        fy = 0.0  # Force in y direction
        
        # Calculate forces from all other particles
        for other in particles:
            if other is self:
                continue
            
            dx = other.x - self.x
            dy = other.y - self.y
            dist_sq = dx*dx + dy*dy
            
            if dist_sq < 0.01:  # Avoid division by zero
                dist_sq = 0.01
            
            dist = math.sqrt(dist_sq)
            
            # Attraction force (gravity-like, weaker at distance)
            if dist > 5.0:  # Only attract if far enough
                force_mag = attraction_strength * self.mass * other.mass / dist_sq
                fx += (dx / dist) * force_mag
                fy += (dy / dist) * force_mag
            
            # Repulsion force (strong at close range, prevents collapse)
            if dist < 8.0:
                repulsion_mag = repulsion_strength / (dist_sq + 0.1)
                fx -= (dx / dist) * repulsion_mag
                fy -= (dy / dist) * repulsion_mag
        
        # Apply forces (F = ma, so a = F/m)
        ax = fx / self.mass
        ay = fy / self.mass
        
        # Update velocity
        self.vx += ax * dt
        self.vy += ay * dt
        
        # Apply damping (friction)
        self.vx *= damping
        self.vy *= damping
        
        # Limit velocity to prevent instability
        max_vel = 100.0
        vel = math.sqrt(self.vx**2 + self.vy**2)
        if vel > max_vel:
            self.vx = (self.vx / vel) * max_vel
            self.vy = (self.vy / vel) * max_vel
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Bounce off walls with energy loss
        margin = self.radius
        if self.x < margin:
            self.x = margin
            self.vx *= -0.7  # Bounce with 70% energy
        elif self.x > width - margin:
            self.x = width - margin
            self.vx *= -0.7
            
        if self.y < margin:
            self.y = margin
            self.vy *= -0.7
        elif self.y > height - margin:
            self.y = height - margin
            self.vy *= -0.7

    # Note: draw method moved to main scene class for batch processing performance

class ParticleSwarm(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        
        self.particles = []
        self.num_particles = 25
        
        # Physics parameters
        self.attraction_strength = 200.0  # How strong particles attract
        self.repulsion_strength = 500.0   # How strong particles repel at close range
        self.damping = 0.98  # Friction (0.98 = 2% energy loss per frame)
        
        # Load palette colors
        self.palette_colors = None
        self.load_palette_colors()
        
    def load_palette_colors(self):
        """Load colors from the selected palette"""
        try:
            palette_mgr = getattr(self.state_manager, '_palette_manager', None)
            if palette_mgr:
                self.palette_colors = self.state_manager.get_palette_colors(palette_mgr)
        except Exception:
            pass
        
        # Fallback colors if no palette
        if not self.palette_colors or len(self.palette_colors) == 0:
            self.palette_colors = [
                (255, 100, 100),  # Red
                (100, 255, 100),  # Green
                (100, 100, 255),  # Blue
                (255, 255, 100),  # Yellow
                (255, 100, 255),  # Magenta
                (100, 255, 255),  # Cyan
            ]
    
    def spawn_particle(self):
        """Spawn a new particle at random position"""
        x = random.uniform(10, self.width - 10)
        y = random.uniform(10, self.height - 10)
        
        # Get color from palette
        color = random.choice(self.palette_colors) if self.palette_colors else (255, 255, 255)
        
        self.particles.append(Particle(x, y, color))
    
    def enter(self, state_manager):
        """Called when scene becomes active"""
        # Spawn initial particles
        for _ in range(self.num_particles):
            self.spawn_particle()
    
    def update(self, dt):
        # Reload palette colors occasionally in case it changed
        if random.random() < 0.01:
            self.load_palette_colors()
        
        # Update all particles
        for particle in self.particles:
            particle.update(dt, self.particles, self.width, self.height,
                          self.attraction_strength, self.repulsion_strength, self.damping)
        
        # Maintain particle count
        while len(self.particles) < self.num_particles:
            self.spawn_particle()
    
    def draw(self, canvas):
        from PIL import Image, ImageDraw
        
        # 1. Create base image for frame (fills background instantly)
        # Dark blue-black background
        img = Image.new('RGB', (self.width, self.height), (10, 10, 20))
        draw = ImageDraw.Draw(img)
        
        # 2. Draw connections (Lines)
        # Optimizing: Draw lines before dots so dots are on top
        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i+1:]:
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                dist_sq = dx*dx + dy*dy
                
                # Draw faint line if particles are close
                if dist_sq < 225.0: # 15^2
                    dist = math.sqrt(dist_sq)
                    alpha = max(0, min(1, 1.0 - dist / 15.0))
                    
                    # Blend with background
                    r = int(10 + (p1.color[0] + p2.color[0]) / 2 * alpha * 0.3)
                    g = int(10 + (p1.color[1] + p2.color[1]) / 2 * alpha * 0.3)
                    b = int(20 + (p1.color[2] + p2.color[2]) / 2 * alpha * 0.3)
                    
                    # Draw Line
                    draw.line([(p1.x, p1.y), (p2.x, p2.y)], fill=(r,g,b), width=1)
        
        # 3. Draw particles (Ellipses)
        for particle in self.particles:
            r, g, b = particle.color
            bbox = [
                particle.x - particle.radius, 
                particle.y - particle.radius, 
                particle.x + particle.radius, 
                particle.y + particle.radius
            ]
            draw.ellipse(bbox, fill=(r,g,b))
            
        # 4. Push to matrix
        canvas.SetImage(img)
