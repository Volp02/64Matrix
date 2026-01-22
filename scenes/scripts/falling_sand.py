from app.core.base_scene import BaseScene
import random
import math

class FallingSand(BaseScene):
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        # Grid stores color tuples (r,g,b) or None for empty
        # 64x64 grid
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.spawn_timer = 0.0
        self.spawn_rate = 0.05
        self.hue_offset = 0.0
        
        # Burst state
        self.bursts = [] # list of dicts: {'x': int, 'timer': float, 'hue': float}
        
        # Performance optimization:
        # Keep track of active height to avoid scanning empty sky
        self.max_y = self.height - 1

    def spawn_sand(self, center_x):
        # Spawn a clump of sand at the top
        # center_x passed from burst logic
        
        # Color variation
        # Sand palette: Yellows, Tans, Oranges, Whites
        base_r = 200
        base_g = 180 + random.randint(-20, 20)
        base_b = 50 + random.randint(0, 50)
        
        # Occasional "colored" sand for visual interest? 
        # brightness variation
        var = random.uniform(0.8, 1.2)
        color = (
            min(255, int(base_r * var)),
            min(255, int(base_g * var)),
            min(255, int(base_b * var))
        )
        
        # Spawn clump
        radius = 1 # Narrow stream
        for y in range(radius):
            for x in range(center_x - radius, center_x + radius):
                if 0 <= x < self.width and 0 <= y < self.height:
                    if random.random() > 0.5: # noisy clump
                        if self.grid[y][x] is None:
                            self.grid[y][x] = color

    def update(self, dt):
        import math # ensure math is avail
        
        # Burst Management
        # randomly start new bursts
        if len(self.bursts) < 3 and random.random() < 0.05: # Max 3 bursts, 5% chance per frame
             self.bursts.append({
                 'x': random.randint(2, self.width-3),
                 'timer': random.uniform(0.5, 1.5),
                 'hue': self.hue_offset + random.randint(0, 100)
             })

        # Process active bursts
        self.spawn_timer += dt
        if self.spawn_timer >= 0.01: 
            self.spawn_timer = 0
            for burst in self.bursts:
                self.spawn_sand(burst['x'])
                burst['timer'] -= 0.01 # Approximate internal tick
        
        # Cleanup expired bursts
        self.bursts = [b for b in self.bursts if b['timer'] > 0]
            
        # Physics Update
        # Iterate from bottom up, left to right (or random x to avoid bias)
        # For simple sand, scanning linear X is usually fine, but alternating X direction helps stack evenness
        
        frame_changes = False
        
        # We scan from y = height-2 down to 0 (checking pixel below)
        # We can stop if we reach top of pile? simplified: scan all
        
        # To avoid bias, we can flip scan order of X each frame
        scan_x = list(range(self.width))
        if int(self.hue_offset) % 2 == 0:
            scan_x.reverse()
            
        # Create a new grid state? 
        # In-place update can cause "teleporting" if we move a pixel down and then process it again in same frame.
        # But iterating Bottom-Up prevents processing the same pixel twice (since it moves into a zone we already processed).
        # So In-Place Bottom-Up is safe for falling.
        
        for y in range(self.height - 2, -1, -1):
            for x in scan_x:
                pixel = self.grid[y][x]
                if pixel is None:
                    continue
                
                # Logic:
                # 1. Try move Down (y+1)
                # 2. Try move Down-Left (y+1, x-1)
                # 3. Try move Down-Right (y+1, x+1)
                
                moved = False
                
                # Check Down
                if self.grid[y+1][x] is None:
                    self.grid[y+1][x] = pixel
                    self.grid[y][x] = None
                    moved = True
                else:
                    # Check diagonals (randomize order to avoid bias?)
                    # If we don't randomize, it will always pile to one side strictly.
                    # Let's check both and pick random available?
                    
                    check_left = (x > 0 and self.grid[y+1][x-1] is None)
                    check_right = (x < self.width - 1 and self.grid[y+1][x+1] is None)
                    
                    if check_left and check_right:
                        # Both open, pick one
                        if random.random() < 0.5:
                            self.grid[y+1][x-1] = pixel
                            self.grid[y][x] = None
                        else:
                            self.grid[y+1][x+1] = pixel
                            self.grid[y][x] = None
                        moved = True
                    elif check_left:
                        self.grid[y+1][x-1] = pixel
                        self.grid[y][x] = None
                        moved = True
                    elif check_right:
                        self.grid[y+1][x+1] = pixel
                        self.grid[y][x] = None
                        moved = True

        # Reset if the pile reaches the top (any pixel stuck at y=0)
        # We check y=0, if any pixel is there, it means it couldn't fall or was just spawned and blocked.
        # But wait, we spawn AT y=0. So we should check if they persist? 
        # Actually simplest is: if y=0 has pixels after physics update, reset.
        if any(self.grid[0][x] is not None for x in range(self.width)):
             self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
                        


    def draw(self, canvas):
        # Optimized draw - only set non-black pixels?
        # Canvas should be cleared by engine usually?
        # If engine clears, we must draw everything.
        canvas.Clear() # Explicit clear
        
        for y in range(self.height):
            for x in range(self.width):
                pixel = self.grid[y][x]
                if pixel:
                    canvas.SetPixel(x, y, pixel[0], pixel[1], pixel[2])
