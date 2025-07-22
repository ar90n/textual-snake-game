"""
Game engine for the Snake Game.
"""

from typing import Tuple, Optional
from textual_snake_game.core.models import Snake, Food, GameState, DIRECTIONS


class GameEngine:
    """Game engine with state management and collision detection."""
    
    def __init__(self, board_width: int = 20, board_height: int = 15, 
                 initial_snake_pos: Tuple[int, int] = (10, 10),
                 initial_snake_length: int = 3):
        """Initialize the game engine with board dimensions and initial state.
        
        Args:
            board_width: Width of the game board
            board_height: Height of the game board
            initial_snake_pos: Starting position of snake head (x, y)
            initial_snake_length: Initial length of the snake
        """
        self.board_width = board_width
        self.board_height = board_height
        
        # Initialize snake
        self.snake = Snake(initial_position=initial_snake_pos, 
                          initial_length=initial_snake_length)
        
        # Initialize food
        self.food = Food(board_width, board_height)
        self.food.place(self.snake)
        
        # Initialize game state
        self.score = 0
        self.game_over = False
    
    def get_state(self) -> GameState:
        """Get the current game state.
        
        Returns:
            GameState object representing current state
        """
        return GameState(
            snake=self.snake,
            food=self.food,
            score=self.score,
            game_over=self.game_over,
            board_width=self.board_width,
            board_height=self.board_height
        )
    
    def set_direction(self, direction: str) -> bool:
        """Set the snake's direction.
        
        Args:
            direction: Direction string ('up', 'down', 'left', 'right')
            
        Returns:
            True if direction was changed, False if invalid
        """
        if direction not in DIRECTIONS:
            return False
        
        return self.snake.set_direction(DIRECTIONS[direction])
    
    def check_wall_collision(self) -> bool:
        """Check if snake has collided with a wall.
        
        Returns:
            True if collision detected, False otherwise
        """
        head_x, head_y = self.snake.get_head()
        
        # Check if head is outside board boundaries
        return (head_x < 0 or head_x >= self.board_width or
                head_y < 0 or head_y >= self.board_height)
    
    def check_food_collision(self) -> bool:
        """Check if snake has collided with food.
        
        Returns:
            True if collision detected, False otherwise
        """
        return self.snake.get_head() == self.food.get_position()
    
    def check_collisions(self) -> Tuple[bool, bool, bool]:
        """Check all collision types.
        
        Returns:
            Tuple of (wall_collision, self_collision, food_collision)
        """
        wall_collision = self.check_wall_collision()
        self_collision = self.snake.check_self_collision()
        food_collision = self.check_food_collision()
        
        return wall_collision, self_collision, food_collision
    
    def get_score(self) -> int:
        """Get the current score.
        
        Returns:
            Current score
        """
        return self.score
    
    def add_score(self, points: int = 1) -> int:
        """Add points to the score.
        
        Args:
            points: Number of points to add (default: 1)
            
        Returns:
            New score after adding points
        """
        self.score += points
        return self.score
    
    def update(self) -> bool:
        """Update game state for one step.
        
        Returns:
            True if game continues, False if game over
        """
        if self.game_over:
            return False
        
        # Calculate where the snake head will be after moving
        head_x, head_y = self.snake.get_head()
        direction = self.snake.get_direction()
        next_head_pos = (head_x + direction[0], head_y + direction[1])
        
        # Check if next position has food
        will_eat_food = next_head_pos == self.food.get_position()
        
        # Move snake (grow if food will be eaten)
        if will_eat_food:
            # When food is eaten:
            # 1. Grow the snake
            self.snake.grow()
            # 2. Place new food
            self.food.place(self.snake)
            # 3. Increment score
            self.add_score()
        else:
            # Normal movement
            self.snake.move()
        
        # Check collisions after moving
        wall_collision, self_collision, _ = self.check_collisions()
        
        # Check for game over conditions
        if wall_collision or self_collision:
            self.game_over = True
            return False
        
        return True
    
    def is_game_over(self) -> bool:
        """Check if the game is over.
        
        Returns:
            True if game is over, False otherwise
        """
        return self.game_over
    
    def end_game(self) -> None:
        """End the game manually."""
        self.game_over = True
    
    def get_final_score(self) -> int:
        """Get the final score when game is over.
        
        Returns:
            Final score if game is over, current score otherwise
        """
        return self.score
    
    def get_game_over_reason(self) -> str:
        """Get the reason for game over.
        
        Returns:
            String describing reason for game over, or empty string if game is not over
        """
        if not self.game_over:
            return ""
        
        # Check wall collision
        if self.check_wall_collision():
            return "Wall collision"
        
        # Check self collision
        if self.snake.check_self_collision():
            return "Self collision"
        
        # If game is over but no specific reason is detected
        return "Game ended"
    
    def reset(self) -> None:
        """Reset the game to initial state."""
        # Re-initialize snake at the center of the board
        self.snake = Snake(initial_position=(self.board_width // 2, self.board_height // 2), 
                          initial_length=3)
        
        # Re-initialize food at a random position not occupied by the snake
        self.food = Food(self.board_width, self.board_height)
        self.food.place(self.snake)
        
        # Reset game state
        self.score = 0
        self.game_over = False