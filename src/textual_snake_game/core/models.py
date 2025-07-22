"""
Data models for the Snake Game.
"""

import random
from typing import List, Tuple, Optional
from dataclasses import dataclass


# Direction vectors for snake movement
DIRECTIONS = {
    'up': (0, -1),
    'down': (0, 1),
    'left': (-1, 0),
    'right': (1, 0)
}


class Snake:
    """Snake data model with movement and collision logic."""
    
    def __init__(self, initial_position: Tuple[int, int] = (10, 10), initial_length: int = 3):
        """Initialize snake with starting position and length.
        
        Args:
            initial_position: Starting position of snake head (x, y)
            initial_length: Initial length of the snake
        """
        self.segments = []
        # Create initial snake segments in a horizontal line
        for i in range(initial_length):
            self.segments.append((initial_position[0] - i, initial_position[1]))
        self.direction = DIRECTIONS['right']  # Start moving right
    
    def get_head(self) -> Tuple[int, int]:
        """Get the head position of the snake.
        
        Returns:
            Tuple of (x, y) coordinates of the snake head
        """
        return self.segments[0]
    
    def get_segments(self) -> List[Tuple[int, int]]:
        """Get all snake segments.
        
        Returns:
            List of (x, y) coordinates for all snake segments
        """
        return self.segments.copy()
    
    def get_direction(self) -> Tuple[int, int]:
        """Get current movement direction.
        
        Returns:
            Direction vector as (dx, dy)
        """
        return self.direction
    
    def set_direction(self, new_direction: Tuple[int, int]) -> bool:
        """Set new movement direction with validation.
        
        Args:
            new_direction: New direction vector (dx, dy)
            
        Returns:
            True if direction was changed, False if invalid
        """
        # Prevent moving in opposite direction (180-degree turn)
        if (new_direction[0] + self.direction[0] == 0 and 
            new_direction[1] + self.direction[1] == 0):
            return False
        
        self.direction = new_direction
        return True
    
    def move(self, grow: bool = False) -> None:
        """Move the snake in the current direction.
        
        Args:
            grow: If True, snake grows (doesn't remove tail)
        """
        # Calculate new head position
        head_x, head_y = self.get_head()
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # Add new head
        self.segments.insert(0, new_head)
        
        # Remove tail unless growing
        if not grow:
            self.segments.pop()
    
    def grow(self) -> None:
        """Grow the snake by one segment."""
        self.move(grow=True)
    
    def check_self_collision(self) -> bool:
        """Check if snake head collides with its body.
        
        Returns:
            True if head collides with body, False otherwise
        """
        head = self.get_head()
        return head in self.segments[1:]  # Check if head is in body segments
    
    def get_length(self) -> int:
        """Get current length of the snake.
        
        Returns:
            Number of segments in the snake
        """
        return len(self.segments)


class Food:
    """Food data model with placement logic."""
    
    def __init__(self, board_width: int, board_height: int):
        """Initialize food with board dimensions.
        
        Args:
            board_width: Width of the game board
            board_height: Height of the game board
        """
        self.board_width = board_width
        self.board_height = board_height
        self.position = (0, 0)  # Will be updated by place method
    
    def get_position(self) -> Tuple[int, int]:
        """Get the current position of the food.
        
        Returns:
            Tuple of (x, y) coordinates of the food
        """
        return self.position
    
    def place(self, snake: Snake) -> Tuple[int, int]:
        """Place food at a random position not occupied by the snake.
        
        Args:
            snake: Snake object to avoid when placing food
            
        Returns:
            Tuple of (x, y) coordinates where food was placed
        """
        snake_segments = snake.get_segments()
        
        # Calculate all possible positions
        all_positions = []
        for x in range(self.board_width):
            for y in range(self.board_height):
                if (x, y) not in snake_segments:
                    all_positions.append((x, y))
        
        # If no valid positions, return None
        if not all_positions:
            # In a real game, this would mean the snake has filled the board
            # For safety, we'll place it at (0,0) but this should never happen
            self.position = (0, 0)
            return self.position
        
        # Choose a random position from valid positions
        self.position = random.choice(all_positions)
        return self.position
    
    def place_efficiently(self, snake: Snake, max_attempts: int = 100) -> Optional[Tuple[int, int]]:
        """Place food efficiently by trying random positions.
        
        This is more efficient for large boards where calculating all positions
        would be expensive. It tries random positions until finding one that
        doesn't overlap with the snake.
        
        Args:
            snake: Snake object to avoid when placing food
            max_attempts: Maximum number of placement attempts
            
        Returns:
            Tuple of (x, y) coordinates where food was placed, or None if failed
        """
        snake_segments = snake.get_segments()
        
        for _ in range(max_attempts):
            # Generate random position
            x = random.randint(0, self.board_width - 1)
            y = random.randint(0, self.board_height - 1)
            
            # Check if position is valid (not on snake)
            if (x, y) not in snake_segments:
                self.position = (x, y)
                return self.position
        
        # If we couldn't find a valid position after max attempts,
        # fall back to the exhaustive method
        return self.place(snake)


@dataclass
class GameState:
    """Game state data structure."""
    snake: Snake                  # Snake object
    food: Food                    # Food object
    score: int                    # Current score
    game_over: bool               # Game over flag
    board_width: int              # Board dimensions
    board_height: int