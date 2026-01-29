from app.core.base_scene import BaseScene
import random
import math

class Ball:
    def __init__(self, x, y, radius, color, life_duration):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.max_life = life_duration
        self.life = life_duration
        
        # Physics State
        self.vx = random.uniform(-60, 60) # Increased Horizontal drift
        self.vy = 0 # Start with 0 vertical velocity (drop)
        
    def is_alive(self):
        return self.life > 0

class PhysicsBalls(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.balls = []
        
        # Physics Constants
        self.gravity = 80.0 # Pixels per second squared
        self.bounce_damping = 0.7 # Lose energy on bounce
        self.friction = 0.995 # Air resistance
        
        # Spawning
        self.spawn_timer = 0
        self.spawn_interval = 1.5 # Slower spawns (was 0.5)
        
    def update(self, dt):
        # dt is already scaled by speed_mult from the engine
        sim_dt = dt
        
        # 2. Spawn Logic
        self.spawn_timer += sim_dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_ball()
            
        # 3. Physics Steps
        # We might want sub-stepping if fast, but simple Euler is okay for this visual
        
        for ball in self.balls:
            # Apply Gravity
            ball.vy += self.gravity * sim_dt
            
            # Apply Drag
            ball.vx *= self.friction
            ball.vy *= self.friction
            
            # Move
            ball.x += ball.vx * sim_dt
            ball.y += ball.vy * sim_dt
            
            # Wall Collisions (X)
            if ball.x - ball.radius < 0:
                ball.x = ball.radius
                ball.vx *= -1 * self.bounce_damping
            elif ball.x + ball.radius >= self.width:
                ball.x = self.width - ball.radius - 1
                ball.vx *= -1 * self.bounce_damping
                
            # Floor Collision (Y)
            if ball.y + ball.radius >= self.height:
                ball.y = self.height - ball.radius - 1
                ball.vy *= -1 * self.bounce_damping
                
                # Stop if moving very slowly on floor
                if abs(ball.vy) < 5:
                    ball.vy = 0
            
            # Ceiling Collision (optional, but good for bouncy balls)
            if ball.y - ball.radius < 0:
                ball.y = ball.radius
                ball.vy *= -1 * self.bounce_damping

            # Lifecycle
            ball.life -= sim_dt

        # 4. Ball-to-Ball Collisions
        self.handle_collisions()

        # Remove dead balls
        self.balls = [b for b in self.balls if b.is_alive()]

    def handle_collisions(self):
        # Simple O(N^2) check
        for i in range(len(self.balls)):
            b1 = self.balls[i]
            for j in range(i + 1, len(self.balls)):
                b2 = self.balls[j]
                
                dx = b2.x - b1.x
                dy = b2.y - b1.y
                dist_sq = dx*dx + dy*dy
                min_dist = b1.radius + b2.radius
                
                if dist_sq < min_dist * min_dist:
                    dist = math.sqrt(dist_sq)
                    if dist == 0: dist = 0.01 # Prevent divide by zero
                    
                    # Normal Vector
                    nx = dx / dist
                    ny = dy / dist
                    
                    # Overlap resolution (move apart)
                    overlap = min_dist - dist
                    total_mass = (b1.radius**3) + (b2.radius**3) # Mass proportional to volume
                    m1_ratio = (b2.radius**3) / total_mass
                    m2_ratio = (b1.radius**3) / total_mass
                    
                    b1.x -= nx * overlap * m1_ratio
                    b1.y -= ny * overlap * m1_ratio
                    b2.x += nx * overlap * m2_ratio
                    b2.y += ny * overlap * m2_ratio
                    
                    # Velocity resolution (Elastic)
                    # Relative velocity
                    dvx = b2.vx - b1.vx
                    dvy = b2.vy - b1.vy
                    
                    # Velocity along normal
                    vel_along_normal = dvx * nx + dvy * ny
                    
                    # If moving apart, skip
                    if vel_along_normal > 0:
                        continue
                        
                    # restitution (bounciness)
                    e = 0.8
                    
                    # Impulse scalar
                    j = -(1 + e) * vel_along_normal
                    j /= (1/(b1.radius**3) + 1/(b2.radius**3))
                    
                    # Apply impulse
                    impulse_x = j * nx
                    impulse_y = j * ny
                    
                    b1.vx -= impulse_x / (b1.radius**3)
                    b1.vy -= impulse_y / (b1.radius**3)
                    b2.vx += impulse_x / (b2.radius**3)
                    b2.vy += impulse_y / (b2.radius**3)

    def spawn_ball(self):
        # Larger balls: 3 to 6 pixels radius
        radius = random.randint(3, 6)
        x = random.randint(radius, self.width - radius)
        y = -radius * 2 
        
        # Get colors from selected palette
        # Try to get palette colors from state_manager
        palette_colors = None
        try:
            # Access palette manager through state_manager's private reference
            palette_mgr = getattr(self.state_manager, '_palette_manager', None)
            if palette_mgr:
                palette_colors = self.state_manager.get_palette_colors(palette_mgr)
        except Exception as e:
            # If palette access fails, fall back to random colors
            pass
        
        if palette_colors and len(palette_colors) > 0:
            # Use random color from palette
            color = random.choice(palette_colors)
        else:
            # Fallback to random colors if no palette available
            color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
        
        life = random.uniform(8.0, 15.0) # Longer life for more interactions
        
        self.balls.append(Ball(x, y, radius, color, life))

    def draw(self, canvas):
        # Clear is handled by engine, but we are drawing to an image now
        from PIL import Image, ImageDraw
        
        # Create a new image for this frame (or reuse a buffer if we wanted to be super optimized, 
        # but creating a 64x64 image is fast enough)
        img = Image.new('RGB', (self.width, self.height), (0,0,0))
        draw = ImageDraw.Draw(img)
        
        for ball in self.balls:
            # Calculate Faded Color
            alpha = max(0, min(1, ball.life / 2.0)) # Fade out in last 2 seconds
            
            r = int(ball.color[0] * alpha)
            g = int(ball.color[1] * alpha)
            b = int(ball.color[2] * alpha)
            
            # Draw Circle using PIL
            # PIL's ellipse is much faster than python loops
            bbox = [
                ball.x - ball.radius, 
                ball.y - ball.radius, 
                ball.x + ball.radius, 
                ball.y + ball.radius
            ]
            draw.ellipse(bbox, fill=(r,g,b))
            
        # Blit the entire image to the canvas at once
        canvas.SetImage(img)
