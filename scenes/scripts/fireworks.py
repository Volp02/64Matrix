from app.core.base_scene import BaseScene
import random
import math

class Particle:
    def __init__(self, x, y, vx, vy, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color  # RGB tuple
        self.life = 1.0  # Start at full brightness
        self.max_life = 1.0
        # Store fade rate per particle for variation
        self.fade_rate = random.uniform(0.4, 0.6)
        
    def update(self, dt, gravity):
        # Apply gravity
        self.vy += gravity * dt
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Fade out over time with per-particle variation
        self.life -= dt * self.fade_rate
        
    def is_alive(self):
        return self.life > 0 and 0 <= self.x < 64 and 0 <= self.y < 64
    
    def get_color(self):
        """Get color with fade applied - brighter at start"""
        r, g, b = self.color
        # Start brighter (boost at beginning, then fade)
        brightness_boost = 1.0 + (1.0 - self.life) * 0.5  # Up to 30% brighter at start
        alpha = max(0, min(1, self.life * brightness_boost))
        return (
            min(255, int(r * alpha)),
            min(255, int(g * alpha)),
            min(255, int(b * alpha))
        )
    
    def draw(self, canvas, width, height):
        """Draw particle as + shape with top/bottom fading faster"""
        px = int(self.x)
        py = int(self.y)
        
        if not (0 <= px < width and 0 <= py < height):
            return
        
        r, g, b = self.color
        base_alpha = max(0, min(1, self.life))
        
        # White glow at center (stronger at start, fades quickly)
        white_alpha = max(0, min(1, self.life * 2.5))  # Fades faster, starts brighter
        white_r = min(255, int(255 * white_alpha * 1.3))  # 20% brighter
        white_g = min(255, int(255 * white_alpha * 1.3))
        white_b = min(255, int(255 * white_alpha * 1.3))
        
        # Draw + shape: center, up, down, left, right
        offsets = [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0)]
        
        for dx, dy in offsets:
            x_pos = px + dx
            y_pos = py + dy
            
            if 0 <= x_pos < width and 0 <= y_pos < height:
                # Top and bottom pixels fade faster (vertical arms)
                if dy != 0:  # Top (dy=-1) or bottom (dy=1)
                    # Fade faster - multiply by additional factor
                    pixel_alpha = base_alpha * 0.7  # 30% faster fade
                else:  # Center or horizontal arms
                    pixel_alpha = base_alpha
                
                # Center pixel is white glow, others are colored
                if dx == 0 and dy == 0:
                    # Blend white glow with color
                    final_r = min(255, int(white_r * 0.7 + r * 0.3 * pixel_alpha))
                    final_g = min(255, int(white_g * 0.7 + g * 0.3 * pixel_alpha))
                    final_b = min(255, int(white_b * 0.7 + b * 0.3 * pixel_alpha))
                else:
                    final_r = int(r * pixel_alpha)
                    final_g = int(g * pixel_alpha)
                    final_b = int(b * pixel_alpha)
                
                canvas.SetPixel(x_pos, y_pos, final_r, final_g, final_b)


class Firework:
    def __init__(self, x, y, color, num_particles=15):
        self.x = x
        self.y = y
        self.color = color
        self.particles = []
        
        # Create particles exploding outward with balanced chaos
        for i in range(num_particles):
            # Start with evenly spaced angles, but add more variation
            base_angle = (i / num_particles) * math.pi * 2
            # More variation in angle (but still somewhat structured)
            angle = base_angle + random.uniform(-0.5, 0.5)
            
            # More variation in speed
            speed = random.uniform(20, 60)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            self.particles.append(Particle(x, y, vx, vy, color))
    
    def update(self, dt, gravity):
        for particle in self.particles:
            particle.update(dt, gravity)
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p.is_alive()]
    
    def is_alive(self):
        return len(self.particles) > 0


class Fireworks(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        
        self.fireworks = []
        self.spawn_timer = 0.0
        self.spawn_interval = random.uniform(1.0, 3.5)  # More random, less frequent
        self.gravity = 50.0  # Slower gravity
        
    def spawn_firework(self):
        """Spawn a new firework at random position"""
        x = random.randint(10, self.width - 10)
        y = random.randint(10, self.height // 2)  # Upper half of screen
        
        # High saturation colors - pick one channel to be high, others lower
        color_type = random.choice(['red', 'green', 'blue', 'yellow', 'cyan', 'magenta'])
        
        if color_type == 'red':
            color = (255, random.randint(0, 100), random.randint(0, 100))
        elif color_type == 'green':
            color = (random.randint(0, 100), 255, random.randint(0, 100))
        elif color_type == 'blue':
            color = (random.randint(0, 100), random.randint(0, 100), 255)
        elif color_type == 'yellow':
            color = (255, 255, random.randint(0, 100))
        elif color_type == 'cyan':
            color = (random.randint(0, 100), 255, 255)
        else:  # magenta
            color = (255, random.randint(0, 100), 255)
        
        # Variable number of particles for more variation
        num_particles = random.randint(12, 20)
        
        self.fireworks.append(Firework(x, y, color, num_particles))
        
        # Set next random spawn time (more random, less frequent)
        self.spawn_interval = random.uniform(1.0, 3.5)
    
    def enter(self, state_manager):
        """Called when scene becomes active"""
        # Spawn initial firework
        self.spawn_firework()
    
    def update(self, dt):
        # Spawn new fireworks at random intervals
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_firework()
        
        # Update all fireworks
        for firework in self.fireworks:
            firework.update(dt, self.gravity)
        
        # Remove dead fireworks
        self.fireworks = [f for f in self.fireworks if f.is_alive()]
    
    def draw(self, canvas):
        # Black background
        for y in range(self.height):
            for x in range(self.width):
                canvas.SetPixel(x, y, 0, 0, 0)
        
        # Draw all particles from all fireworks
        for firework in self.fireworks:
            for particle in firework.particles:
                particle.draw(canvas, self.width, self.height)
