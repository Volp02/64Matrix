from app.core.base_scene import BaseScene
import random


class SnakeGame(BaseScene):
    """
    Classic Snake game with auto-play.
    Snake moves in grid, grows when eating food, game over on collision.
    """
    
    def __init__(self, matrix, state_manager):
        super().__init__(matrix, state_manager)
        
        # Grid-based movement (1 pixel per cell)
        self.cell_size = 1
        
        # Snake properties
        self.snake = []
        self.direction = (1, 0)  # Right
        self.next_direction = (1, 0)
        
        # Game state
        self.game_over = False
        self.score = 0
        self.move_timer = 0.0
        self.move_interval = 0.15  # Move every 0.15 seconds
        
        # Food
        self.food = None
        
        # Initialize game
        self._reset_game()
    
    def _reset_game(self):
        """Reset game to initial state"""
        # Start snake in center, 3 segments long
        center_x = self.width // 2
        center_y = self.height // 2
        
        self.snake = [
            (center_x - 2, center_y),
            (center_x - 1, center_y),
            (center_x, center_y),
        ]
        
        self.direction = (1, 0)  # Right
        self.next_direction = (1, 0)
        self.game_over = False
        self.score = 0
        self.move_timer = 0.0
        
        # Spawn food
        self._spawn_food()
    
    def _spawn_food(self):
        """Spawn food at random location (not on snake)"""
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            # Check if position is not on snake
            if (x, y) not in self.snake:
                self.food = (x, y)
                break
    
    def _get_next_head_position(self):
        """Calculate next head position based on direction"""
        head_x, head_y = self.snake[-1]
        dx, dy = self.next_direction
        return (head_x + dx, head_y + dy)
    
    def _check_collision(self, pos):
        """Check if position collides with walls or snake body"""
        x, y = pos
        
        # Wall collision
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        
        # Self collision (check all but tail, which will move)
        if pos in self.snake[:-1]:
            return True
        
        return False
    
    def _auto_steer(self):
        """Improved AI: prioritize moving toward food, avoid collisions"""
        if not self.food:
            return
        
        head_x, head_y = self.snake[-1]
        food_x, food_y = self.food
        
        # Calculate current distance to food
        current_dist = abs(food_x - head_x) + abs(food_y - head_y)
        
        # Evaluate all possible directions
        all_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        best_dir = None
        best_score = -999999
        
        for candidate_dir in all_directions:
            # Can't reverse direction
            if candidate_dir == (-self.direction[0], -self.direction[1]):
                continue
            
            # Check if this direction is safe
            next_pos = self._get_next_head_position_with_dir(candidate_dir)
            if self._check_collision(next_pos):
                continue  # Skip unsafe directions
            
            # Calculate new distance to food after moving this direction
            new_x = head_x + candidate_dir[0]
            new_y = head_y + candidate_dir[1]
            new_dist = abs(food_x - new_x) + abs(food_y - new_y)
            
            # Score: prefer directions that get closer to food
            # Higher score = better direction
            score = current_dist - new_dist  # Positive if getting closer
            
            # Small bonus for continuing in current direction (smoother movement)
            if candidate_dir == self.direction:
                score += 0.5
            
            # Pick the best direction
            if score > best_score:
                best_score = score
                best_dir = candidate_dir
        
        # If we found a good direction, use it
        if best_dir is not None:
            self.next_direction = best_dir
        # Otherwise, try to continue in current direction if safe
        elif not self._check_collision(self._get_next_head_position_with_dir(self.direction)):
            self.next_direction = self.direction
    
    def _get_next_head_position_with_dir(self, direction):
        """Calculate next head position with given direction"""
        head_x, head_y = self.snake[-1]
        dx, dy = direction
        return (head_x + dx, head_y + dy)
    
    def update(self, dt):
        if self.game_over:
            # Reset after a delay
            self.move_timer += dt
            if self.move_timer >= 2.0:  # Wait 2 seconds before reset
                self._reset_game()
            return
        
        self.move_timer += dt
        
        if self.move_timer >= self.move_interval:
            self.move_timer = 0.0
            
            # Auto-steer towards food (updates next_direction)
            self._auto_steer()
            
            # Update direction
            self.direction = self.next_direction
            
            # Calculate next head position
            next_head = self._get_next_head_position()
            
            # Check collision
            if self._check_collision(next_head):
                self.game_over = True
                self.move_timer = 0.0
                return
            
            # Move snake
            self.snake.append(next_head)
            
            # Check if food eaten
            if next_head == self.food:
                self.score += 1
                self._spawn_food()
                # Don't remove tail (snake grows)
            else:
                # Remove tail
                self.snake.pop(0)
    
    def draw(self, canvas):
        # Dark background
        canvas.Fill(5, 5, 10)
        
        if self.game_over:
            # Flash snake red when game over
            flash = int((self.move_timer * 10) % 2)
            if flash:
                snake_color = (200, 0, 0)  # Red
            else:
                snake_color = (100, 150, 255)  # Blue
        else:
            snake_color = (100, 255, 100)  # Green snake
        
        # Draw snake
        for i, segment in enumerate(self.snake):
            x, y = segment
            
            # Head is slightly brighter
            if i == len(self.snake) - 1:
                r, g, b = snake_color
                r = min(255, r + 50)
                g = min(255, g + 50)
                b = min(255, b + 50)
            else:
                r, g, b = snake_color
            
            if 0 <= x < self.width and 0 <= y < self.height:
                canvas.SetPixel(x, y, r, g, b)
        
        # Draw food (red)
        if self.food:
            fx, fy = self.food
            if 0 <= fx < self.width and 0 <= fy < self.height:
                canvas.SetPixel(fx, fy, 255, 50, 50)
