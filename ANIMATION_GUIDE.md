# Animation Development Guide for 64x64 LED Matrix

## Overview

This guide will teach you how to create custom animations for your 64x64 RGB LED matrix display running on Raspberry Pi. The system uses Python scripts that inherit from `BaseScene` and are automatically loaded from the `scenes/scripts/` directory.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Device Specifications](#device-specifications)
3. [Basic Structure](#basic-structure)
4. [Core Concepts](#core-concepts)
5. [Drawing Methods](#drawing-methods)
6. [Using Color Palettes](#using-color-palettes)
7. [Speed Control](#speed-control)
8. [Example Animations](#example-animations)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Create Your Script File

Create a new Python file in `scenes/scripts/` with a descriptive name:

```python
# scenes/scripts/my_animation.py
from app.core.base_scene import BaseScene

class MyAnimation(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        # Initialize your animation here
        
    def update(self, dt):
        # Update animation logic here
        pass
        
    def draw(self, canvas):
        # Draw your animation here - THIS IS REQUIRED
        pass
```

### 2. Required Methods

- **`__init__(matrix, state_manager)`**: Initialize your animation
- **`draw(canvas)`**: **REQUIRED** - Draw your animation every frame
- **`update(dt)`**: Optional - Update animation logic every frame

### 3. File Naming

- Use descriptive names: `fireworks.py`, `matrix_rain.py`, `spiral.py`
- The filename (without `.py`) appears in the Library view
- Avoid spaces and special characters (use underscores)

---

## Device Specifications

### Matrix Dimensions

- **Size**: 64x64 pixels
- **Coordinates**: 
  - X-axis: 0 (left) to 63 (right)
  - Y-axis: 0 (top) to 63 (bottom)
  - **Origin**: Top-left corner (0, 0)

### Performance

- **Frame Rate**: ~60 FPS
- **Platform**: Raspberry Pi (plenty of processing power)
- **Delta Time**: `dt` is passed in **seconds** (typically ~0.016s at 60 FPS)

### Coordinate System

- Use **integer coordinates** for pixel drawing
- **Float coordinates** are fine for calculations, but convert to `int()` when drawing
- Always check bounds: `0 <= x < 64` and `0 <= y < 64`

---

## Basic Structure

### Minimal Working Animation

```python
from app.core.base_scene import BaseScene

class MinimalAnimation(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.x = 32  # Center of 64x64 display
        self.y = 32
        
    def update(self, dt):
        # Optional: Update logic
        pass
        
    def draw(self, canvas):
        # REQUIRED: Draw something
        canvas.SetPixel(self.x, self.y, 255, 0, 0)  # Red pixel
```

### What You Get from BaseScene

When you inherit from `BaseScene`, you automatically get:

```python
self.matrix      # MatrixDriver instance
self.state_manager  # StateManager instance (settings, palettes)
self.canvas      # Drawing canvas (RGBMatrix canvas)
self.width       # 64
self.height      # 64
```

---

## Core Concepts

### Frame-Rate Independence

**ALWAYS** use `dt` (delta time) for movement and timers:

```python
def update(self, dt):
    # ✅ GOOD: Frame-rate independent
    self.x += 50.0 * dt  # Moves 50 pixels per second
    
    # ❌ BAD: Frame-rate dependent
    self.x += 1  # Speed depends on FPS
```

### Bounds Checking

**ALWAYS** check bounds before drawing:

```python
def draw(self, canvas):
    x = int(self.x)
    y = int(self.y)
    
    # ✅ GOOD: Safe drawing
    if 0 <= x < self.width and 0 <= y < self.height:
        canvas.SetPixel(x, y, 255, 0, 0)
    
    # ❌ BAD: Can crash if out of bounds
    canvas.SetPixel(x, y, 255, 0, 0)  # May crash!
```

### Lifecycle Methods

```python
def __init__(self, matrix, state_manager):
    """Called when scene is instantiated"""
    super().__init__(matrix, state_manager)
    # Initialize your animation state

def update(self, dt):
    """Called every frame before draw()"""
    # Update logic, physics, timers, etc.

def draw(self, canvas):
    """Called every frame after update() - REQUIRED"""
    # Draw your animation

def enter(self, state_manager):
    """Called when scene becomes active (optional)"""
    # Reset state, spawn initial objects, etc.

def exit(self):
    """Called when scene is being replaced (optional)"""
    # Cleanup resources
```

---

## Drawing Methods

### SetPixel(x, y, r, g, b)

Draw a single pixel:

```python
def draw(self, canvas):
    # Draw a red pixel at (10, 20)
    canvas.SetPixel(10, 20, 255, 0, 0)
    
    # Draw a green pixel at (30, 40)
    canvas.SetPixel(30, 40, 0, 255, 0)
    
    # Draw a blue pixel at (50, 60)
    canvas.SetPixel(50, 60, 0, 0, 255)
```

**Parameters:**
- `x, y`: Integer coordinates (0-63)
- `r, g, b`: Color components (0-255)

### Fill(r, g, b)

Fill entire canvas (usually not needed - engine clears automatically):

```python
def draw(self, canvas):
    canvas.Fill(0, 0, 0)  # Fill with black
    canvas.Fill(255, 255, 255)  # Fill with white
```

### Clear()

Clear canvas to black (usually not needed):

```python
def draw(self, canvas):
    canvas.Clear()  # Same as Fill(0, 0, 0)
```

### Drawing Shapes

The canvas doesn't have built-in shapes, so you implement them yourself:

#### Drawing a Filled Circle

```python
def draw_circle(self, canvas, cx, cy, radius, r, g, b):
    """Draw a filled circle"""
    min_x = int(cx - radius)
    max_x = int(cx + radius)
    min_y = int(cy - radius)
    max_y = int(cy + radius)
    
    r_sq = radius * radius
    
    for cy_pixel in range(min_y, max_y + 1):
        for cx_pixel in range(min_x, max_x + 1):
            if 0 <= cx_pixel < self.width and 0 <= cy_pixel < self.height:
                dx = cx_pixel - cx
                dy = cy_pixel - cy
                if dx*dx + dy*dy <= r_sq:
                    canvas.SetPixel(cx_pixel, cy_pixel, r, g, b)
```

#### Drawing a Filled Rectangle

```python
def draw_rect(self, canvas, x, y, width, height, r, g, b):
    """Draw a filled rectangle"""
    for py in range(y, y + height):
        for px in range(x, x + width):
            if 0 <= px < self.width and 0 <= py < self.height:
                canvas.SetPixel(px, py, r, g, b)
```

#### Drawing a Line

```python
def draw_line(self, canvas, x1, y1, x2, y2, r, g, b):
    """Bresenham's line algorithm"""
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
```

---

## Using Color Palettes

### Getting Palette Colors

Access colors from the currently selected palette:

```python
def spawn_particle(self):
    # Get palette colors
    palette_colors = None
    try:
        palette_mgr = getattr(self.state_manager, '_palette_manager', None)
        if palette_mgr:
            palette_colors = self.state_manager.get_palette_colors(palette_mgr)
    except Exception:
        pass
    
    # Use palette color or fallback
    if palette_colors and len(palette_colors) > 0:
        color = random.choice(palette_colors)
    else:
        color = (255, 255, 255)  # White fallback
    
    # Use color
    canvas.SetPixel(x, y, color[0], color[1], color[2])
```

**What you get:**
- `palette_colors`: List of RGB tuples `[(r, g, b), ...]` or `None`
- Colors are automatically converted from hex to RGB
- Always provide a fallback color

### Example: Using Palette in Animation

```python
class PaletteAwareAnimation(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.particles = []
        
    def spawn_particle(self):
        # Get palette colors
        palette_colors = None
        try:
            palette_mgr = getattr(self.state_manager, '_palette_manager', None)
            if palette_mgr:
                palette_colors = self.state_manager.get_palette_colors(palette_mgr)
        except Exception:
            pass
        
        # Use random color from palette
        if palette_colors and len(palette_colors) > 0:
            color = random.choice(palette_colors)
        else:
            color = (255, 200, 0)  # Orange fallback
        
        self.particles.append({
            'x': 32, 'y': 32,
            'color': color
        })
```

---

## Speed Control

### Respecting the Speed Setting

**IMPORTANT:** The engine automatically scales `dt` by the speed setting before calling `update()`. The `dt` parameter you receive is **already scaled** by the speed multiplier.

You can use `dt` directly for time-based operations:

```python
def update(self, dt):
    # dt is already scaled by speed setting (0.1 to 2.0)
    # Use it directly for frame-rate independent movement
    self.x += self.vx * dt
    self.timer += dt
    self.spawn_timer += dt
```

**Note:** If you need to access the raw speed multiplier for other purposes, you can still get it:

```python
def update(self, dt):
    # dt is already scaled, but you can get the multiplier if needed
    settings = self.state_manager.get_settings()
    speed_mult = settings.get("speed", 1.0)
    
    # Use dt directly (already scaled)
    self.x += self.vx * dt
    self.timer += dt
```

### Example: Speed-Aware Animation

```python
class SpeedAwareAnimation(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.x = 0.0
        self.vx = 50.0  # pixels per second
        
    def update(self, dt):
        # dt is already scaled by speed setting, use it directly
        # Movement automatically respects speed setting
        self.x += self.vx * dt
        
        # Wrap around
        if self.x > self.width:
            self.x = 0
```

---

## Example Animations

### Example 1: Simple Bouncing Ball

Based on `bouncing_ball.py`:

```python
from app.core.base_scene import BaseScene
import random

class BouncingBall(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.x = 10.0
        self.y = 10.0
        self.vx = 20.0  # pixels per second
        self.vy = 15.0
        self.radius = 2
        self.color = (255, 0, 0)  # Red
        
    def update(self, dt):
        # Move
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Bounce X
        if self.x <= 0 or self.x >= self.width:
            self.vx *= -1
            self.x = max(0, min(self.x, self.width))
            self.color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
            
        # Bounce Y
        if self.y <= 0 or self.y >= self.height:
            self.vy *= -1
            self.y = max(0, min(self.y, self.height))
            self.color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )

    def draw(self, canvas):
        # Draw ball as 2x2 square
        ix = int(self.x)
        iy = int(self.y)
        r, g, b = self.color
        
        canvas.SetPixel(ix, iy, r, g, b)
        canvas.SetPixel(ix + 1, iy, r, g, b)
        canvas.SetPixel(ix, iy + 1, r, g, b)
        canvas.SetPixel(ix + 1, iy + 1, r, g, b)
```

### Example 2: Physics Balls with Collisions

Based on `physics_balls.py`:

```python
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
        self.vx = random.uniform(-60, 60)
        self.vy = 0  # Start with 0 vertical velocity
        
    def is_alive(self):
        return self.life > 0

class PhysicsBalls(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.balls = []
        self.gravity = 80.0
        self.bounce_damping = 0.7
        self.friction = 0.995
        self.spawn_timer = 0
        self.spawn_interval = 1.5
        
    def update(self, dt):
        # dt is already scaled by speed setting from the engine
        # Spawn new ball
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_ball()
        
        # Update physics
        for ball in self.balls:
            ball.vy += self.gravity * dt
            ball.vx *= self.friction
            ball.vy *= self.friction
            ball.x += ball.vx * dt
            ball.y += ball.vy * dt
            
            # Collisions with walls
            if ball.x - ball.radius < 0:
                ball.x = ball.radius
                ball.vx *= -1 * self.bounce_damping
            elif ball.x + ball.radius >= self.width:
                ball.x = self.width - ball.radius - 1
                ball.vx *= -1 * self.bounce_damping
                
            if ball.y + ball.radius >= self.height:
                ball.y = self.height - ball.radius - 1
                ball.vy *= -1 * self.bounce_damping
                if abs(ball.vy) < 5:
                    ball.vy = 0
            
            if ball.y - ball.radius < 0:
                ball.y = ball.radius
                ball.vy *= -1 * self.bounce_damping
            
            ball.life -= dt
        
        # Handle ball-to-ball collisions
        self.handle_collisions()
        
        # Remove dead balls
        self.balls = [b for b in self.balls if b.is_alive()]
    
    def handle_collisions(self):
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
                    if dist == 0:
                        dist = 0.01
                    
                    # Normal vector
                    nx = dx / dist
                    ny = dy / dist
                    
                    # Overlap resolution
                    overlap = min_dist - dist
                    total_mass = (b1.radius**3) + (b2.radius**3)
                    m1_ratio = (b2.radius**3) / total_mass
                    m2_ratio = (b1.radius**3) / total_mass
                    
                    b1.x -= nx * overlap * m1_ratio
                    b1.y -= ny * overlap * m1_ratio
                    b2.x += nx * overlap * m2_ratio
                    b2.y += ny * overlap * m2_ratio
                    
                    # Velocity resolution
                    dvx = b2.vx - b1.vx
                    dvy = b2.vy - b1.vy
                    vel_along_normal = dvx * nx + dvy * ny
                    
                    if vel_along_normal > 0:
                        continue
                    
                    e = 0.8  # Restitution
                    j = -(1 + e) * vel_along_normal
                    j /= (1/(b1.radius**3) + 1/(b2.radius**3))
                    
                    impulse_x = j * nx
                    impulse_y = j * ny
                    
                    b1.vx -= impulse_x / (b1.radius**3)
                    b1.vy -= impulse_y / (b1.radius**3)
                    b2.vx += impulse_x / (b2.radius**3)
                    b2.vy += impulse_y / (b2.radius**3)
    
    def spawn_ball(self):
        radius = random.randint(3, 6)
        x = random.randint(radius, self.width - radius)
        y = -radius * 2
        
        # Get palette colors
        palette_colors = None
        try:
            palette_mgr = getattr(self.state_manager, '_palette_manager', None)
            if palette_mgr:
                palette_colors = self.state_manager.get_palette_colors(palette_mgr)
        except Exception:
            pass
        
        if palette_colors and len(palette_colors) > 0:
            color = random.choice(palette_colors)
        else:
            color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
        
        life = random.uniform(8.0, 15.0)
        self.balls.append(Ball(x, y, radius, color, life))
    
    def draw(self, canvas):
        for ball in self.balls:
            # Fade out based on life
            alpha = max(0, min(1, ball.life / 2.0))
            
            r = int(ball.color[0] * alpha)
            g = int(ball.color[1] * alpha)
            b = int(ball.color[2] * alpha)
            
            # Draw filled circle
            min_x = int(ball.x - ball.radius)
            max_x = int(ball.x + ball.radius)
            min_y = int(ball.y - ball.radius)
            max_y = int(ball.y + ball.radius)
            r_sq = ball.radius * ball.radius
            
            for cy in range(min_y, max_y + 1):
                for cx in range(min_x, max_x + 1):
                    if 0 <= cx < self.width and 0 <= cy < self.height:
                        dx = cx - ball.x
                        dy = cy - ball.y
                        if dx*dx + dy*dy <= r_sq:
                            canvas.SetPixel(cx, cy, r, g, b)
```

### Example 3: Simple Moving Square

Based on `test_simple.py`:

```python
from app.core.base_scene import BaseScene
import random

class SimpleSquare(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        self.x = self.width // 2
        self.y = self.height // 2
        self.vx = 30.0
        self.vy = 25.0
        self.size = 5
        self.color = (255, 0, 0)
        
    def update(self, dt):
        # dt is already scaled by speed setting
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Bounce off walls
        if self.x - self.size <= 0 or self.x + self.size >= self.width:
            self.vx *= -1
            self.x = max(self.size, min(self.x, self.width - self.size))
            self.color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
            
        if self.y - self.size <= 0 or self.y + self.size >= self.height:
            self.vy *= -1
            self.y = max(self.size, min(self.y, self.height - self.size))
            self.color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )

    def draw(self, canvas):
        r, g, b = self.color
        center_x = int(self.x)
        center_y = int(self.y)
        
        # Draw filled square
        for dy in range(-self.size, self.size + 1):
            for dx in range(-self.size, self.size + 1):
                px = center_x + dx
                py = center_y + dy
                if 0 <= px < self.width and 0 <= py < self.height:
                    canvas.SetPixel(px, py, r, g, b)
```

---

## Best Practices

### 1. Frame-Rate Independence

**ALWAYS** use `dt` for movement:

```python
# ✅ GOOD
self.x += self.vx * dt

# ❌ BAD
self.x += 1
```

### 2. Bounds Checking

**ALWAYS** check bounds before drawing:

```python
# ✅ GOOD
if 0 <= x < self.width and 0 <= y < self.height:
    canvas.SetPixel(x, y, r, g, b)

# ❌ BAD
canvas.SetPixel(x, y, r, g, b)  # May crash!
```

### 3. Speed Setting

The engine automatically applies the speed multiplier to `dt` before calling `update()`, so you can use `dt` directly:

```python
# ✅ GOOD - dt is already scaled by speed setting
self.x += self.vx * dt

# ✅ ALSO GOOD - If you need the raw multiplier for other purposes
settings = self.state_manager.get_settings()
speed_mult = settings.get("speed", 1.0)
# But remember: dt is already scaled, so don't multiply again unless you have a specific reason
```

### 4. Error Handling

Handle errors gracefully:

```python
def draw(self, canvas):
    try:
        # Your drawing code
        canvas.SetPixel(x, y, r, g, b)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error in draw: {e}")
```

### 5. Performance

- Keep `draw()` fast - avoid heavy calculations
- Pre-calculate values in `update()` when possible
- Limit the number of objects (64x64 is small, but Raspberry Pi can handle more)

### 6. Initialization

Use `enter()` to spawn initial content:

```python
def enter(self, state_manager):
    """Called when scene becomes active"""
    # Spawn initial particles/objects for immediate visibility
    for _ in range(5):
        self.spawn_particle()
```

### 7. Color Format

Colors are RGB tuples `(r, g, b)` with values 0-255:

```python
# ✅ GOOD
color = (255, 128, 0)  # Orange
canvas.SetPixel(x, y, color[0], color[1], color[2])

# ❌ BAD
color = (1.0, 0.5, 0.0)  # Wrong format (0-1 instead of 0-255)
```

---

## Troubleshooting

### Animation doesn't appear

1. **Check file location**: Must be in `scenes/scripts/`
2. **Check class name**: Must inherit from `BaseScene`
3. **Check method names**: `draw()` is required, must be lowercase
4. **Check for errors**: Look at server logs for Python errors
5. **Ensure you're drawing something**: The `draw()` method must call `canvas.SetPixel()` at least once

### Animation is black/empty

1. **Check if `draw()` is being called**: Add a print statement or always draw at least one pixel
2. **Check bounds**: Make sure coordinates are within 0-63
3. **Check color values**: Ensure RGB values are 0-255, not 0-1
4. **Check initialization**: Use `enter()` to spawn initial content

### Animation is too fast/slow

- Use `dt` (delta time) for all time-based operations
- Respect the `speed` setting from `state_manager.get_settings()`

### Colors look wrong

- RGB values are 0-255, not 0-1
- Check that you're using `(r, g, b)` tuples correctly
- Try using palette colors for consistent results

### Performance issues

- Limit the number of objects/particles
- Avoid heavy calculations in `draw()`
- Pre-calculate values in `update()`
- Raspberry Pi can handle more, but keep it reasonable

### Palette colors return None

- Always provide a fallback color
- Check that `_palette_manager` exists: `getattr(self.state_manager, '_palette_manager', None)`
- Handle the case when no palette is selected

---

## Common Patterns

### Pattern 1: Spawning Objects

```python
def update(self, dt):
    # dt is already scaled by speed setting
    self.spawn_timer += dt
    if self.spawn_timer >= self.spawn_interval:
        self.spawn_timer = 0
        self.spawn_object()
```

### Pattern 2: Lifecycle Management

```python
def update(self, dt):
    # Update objects
    for obj in self.objects:
        obj.update(dt)
        obj.life -= dt
    
    # Remove dead objects
    self.objects = [obj for obj in self.objects if obj.life > 0]
```

### Pattern 3: Fade Out Effect

```python
def draw(self, canvas):
    for obj in self.objects:
        # Calculate fade based on life
        alpha = max(0, min(1, obj.life / obj.max_life))
        r = int(obj.color[0] * alpha)
        g = int(obj.color[1] * alpha)
        b = int(obj.color[2] * alpha)
        canvas.SetPixel(int(obj.x), int(obj.y), r, g, b)
```

### Pattern 4: Bouncing Physics

```python
def update(self, dt):
    # Move
    self.x += self.vx * dt
    self.y += self.vy * dt
    
    # Bounce off walls
    if self.x <= 0 or self.x >= self.width:
        self.vx *= -1
        self.x = max(0, min(self.x, self.width))
```

---

## Summary

1. **Inherit from `BaseScene`** and implement `draw()`
2. **Use `dt`** for frame-rate independent animations (already scaled by speed setting)
3. **Check bounds** before drawing pixels
4. **Speed is automatic** - `dt` is already scaled by the speed setting
5. **Use palettes** for consistent, user-selectable colors
6. **Keep `draw()` fast** - do heavy calculations in `update()`
7. **Handle errors gracefully** - don't crash the system
8. **Initialize content** in `enter()` for immediate visibility

Happy animating! 🎨✨
