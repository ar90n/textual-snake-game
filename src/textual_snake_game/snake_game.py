"""
Simple Snake Game using Textual framework.

This module contains the main SnakeGame application class that integrates all components
and manages the application lifecycle.
"""

from typing import Dict, Optional

# Import Textual components
from textual.app import App
from textual import events

# Import models and game engine
from textual_snake_game.core.game_engine import GameEngine
from textual_snake_game.core.models import Snake
from textual_snake_game.ui.ui_components import GameScreen


class SnakeGame(App):
    """Main Snake Game application.
    
    This class serves as the main application entry point and integrates all components
    of the snake game. It manages:
    - Application lifecycle (initialization, mounting, unmounting)
    - Game state updates and timer management
    - User input handling
    - Screen management and transitions
    """
    
    # Key mappings for direction control
    KEY_MAPPINGS: Dict[str, str] = {
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
        "w": "up",
        "s": "down",
        "a": "left",
        "d": "right",
    }
    
    # Game speed settings (in seconds between updates)
    GAME_SPEEDS = {
        "slow": 0.3,
        "normal": 0.2,
        "fast": 0.1,
    }
    
    def __init__(self, board_width: int = 20, board_height: int = 15):
        """Initialize the Snake Game application.
        
        Args:
            board_width: Width of the game board (default: 20)
            board_height: Height of the game board (default: 15)
        """
        super().__init__()
        self.title = "Snake Game"
        self.board_width = board_width
        self.board_height = board_height
        self.game_engine = None
        self.game_screen = None
        self.paused = False
        self.last_direction: Optional[str] = None
        self.game_speed = "normal"
        self.game_timer = None  # Store the game timer
        
    def on_mount(self) -> None:
        """Initialize the game when the app is mounted."""
        # Initialize game engine with board dimensions
        self.game_engine = GameEngine(
            board_width=self.board_width,
            board_height=self.board_height,
            initial_snake_pos=(self.board_width // 2, self.board_height // 2),
            initial_snake_length=3
        )
        
        # Initialize game state (snake position, food placement, score)
        initial_state = self.game_engine.get_state()
        
        # Create and push the game screen with initial state
        self.game_screen = GameScreen(initial_state)
        self.push_screen(self.game_screen)
        
        # Set up game timer for smooth movement
        self._setup_game_timer()
        
        # Schedule the game initialization to happen after the screen is fully mounted
        self.call_after_refresh(self.initialize_game)
    
    def start_game_timer(self, interval: float) -> None:
        """Start the game timer with the specified interval.
        
        Args:
            interval: Time in seconds between game updates
        """
        # Stop existing timer if any
        if self.game_timer:
            self.game_timer.stop()
        
        # Create a repeating timer
        def repeating_update():
            self.update_game()
            # Reschedule the timer if game is still running
            if not self.game_engine.is_game_over() and not self.paused:
                self.game_timer = self.set_timer(interval, repeating_update, pause=False)
        
        # Start the timer
        self.game_timer = self.set_timer(interval, repeating_update, pause=False)
    
    def stop_game_timer(self) -> None:
        """Stop the game timer."""
        if not self.game_timer:
            return
            
        self.game_timer.stop()
        self.game_timer = None
    
    def _setup_game_timer(self) -> None:
        """Set up the game timer with the current speed setting.
        
        This method creates a periodic timer that calls update_game at regular intervals
        based on the current game speed setting. If a timer already exists, it is stopped
        before creating a new one.
        """
        # Get the interval for current speed
        interval = self.GAME_SPEEDS[self.game_speed]
        # Start the game timer
        self.start_game_timer(interval)
    
    def set_game_speed(self, speed: str) -> bool:
        """Set the game speed.
        
        Args:
            speed: Speed setting ("slow", "normal", or "fast")
            
        Returns:
            True if speed was changed, False if invalid
        """
        if speed not in self.GAME_SPEEDS:
            return False
            
        self.game_speed = speed
        
        # Update the timer with new speed if it exists
        if self.game_timer:
            self._setup_game_timer()
            
        return True
    
    def on_key(self, event: events.Key) -> None:
        """Handle keyboard input for snake direction.
        
        Args:
            event: Key event from Textual
        """
        # Skip if game is over or paused
        if self.game_engine is None or self.game_engine.is_game_over() or self.paused:
            return
        
        # Check if key is a valid direction
        key = event.key
        if key in self.KEY_MAPPINGS:
            direction = self.KEY_MAPPINGS[key]
            
            # Validate the move (prevent 180-degree turns)
            # The actual validation is done in the snake.set_direction method
            # which is called by game_engine.set_direction
            result = self.game_engine.set_direction(direction)
            
            # Store the last valid direction
            if result:
                self.last_direction = direction
            return
        
        # Speed control keys
        speed_keys = {"1": "slow", "2": "normal", "3": "fast"}
        if key in speed_keys:
            self.set_game_speed(speed_keys[key])
    
    def update_game(self) -> None:
        """Update game state on timer tick.
        
        This method is called periodically by the game timer to update the game state
        and refresh the UI. It handles the main game loop logic including:
        - Updating the game state through the game engine
        - Refreshing the UI with the new state
        - Handling game over conditions
        
        The update is skipped if the game is paused or already over.
        """
        if not self.game_engine or self.paused or self.game_engine.is_game_over():
            return
            
        # Update game state
        game_continues = self.game_engine.update()
        
        # If game just ended, handle game over state
        if not game_continues:
            self.game_engine.end_game()
            
        # Update UI with new state (handles both normal and game-over states)
        if self.game_screen:
            self.game_screen.update_game_state(self.game_engine.get_state())
    
    def start_new_game(self) -> None:
        """Start a new game with initial settings.
        
        This method initializes a new game with:
        - Snake at initial position and length
        - Food placed at a random position
        - Score set to 0
        - Game over flag cleared
        
        Uses the initialize_game method to ensure consistent initialization
        across both initial startup and game resets.
        """
        # Use the initialize_game method for consistent game initialization
        self.initialize_game()
    
    def reset_game(self) -> None:
        """Reset the game to initial state.
        
        This method resets the game to its initial state, including:
        - Resetting the snake to its initial position and length
        - Placing new food at a random position
        - Resetting the score to 0
        - Clearing the game over flag
        - Resetting game control state (pause, direction)
        """
        # Use the start_new_game method to reset the game
        self.start_new_game()
    
    def toggle_pause(self) -> None:
        """Toggle game pause state."""
        self.paused = not self.paused
    
    def initialize_game(self) -> None:
        """Initialize the game with proper startup settings.
        
        This method handles the initial game setup:
        - Ensures snake is properly placed at the starting position
        - Ensures food is placed at a valid random position
        - Sets up the initial score display with a value of 0
        - Configures the game state for a new game
        
        This satisfies requirements 1.1 (initial snake display), 
        2.1 (random food placement), and 3.1 (initial score of 0).
        """
        # Define initial snake position at the center of the board
        initial_snake_pos = (self.board_width // 2, self.board_height // 2)
        initial_snake_length = 3
        
        if not self.game_engine:
            # Create game engine if it doesn't exist
            self.game_engine = GameEngine(
                board_width=self.board_width,
                board_height=self.board_height,
                initial_snake_pos=initial_snake_pos,
                initial_snake_length=initial_snake_length
            )
        else:
            # Reset the game engine to ensure proper initial state
            self.game_engine.reset()
            
            # Explicitly ensure snake is at the correct position with correct length
            self.game_engine.snake = Snake(
                initial_position=initial_snake_pos,
                initial_length=initial_snake_length
            )
            
            # Ensure food is placed at a valid position (not on snake)
            self.game_engine.food.place(self.game_engine.snake)
        
        # Explicitly set score to 0 to satisfy requirement 3.1
        self.game_engine.score = 0
        
        # Get the initial state with snake and food properly positioned
        initial_state = self.game_engine.get_state()
        
        # Create game screen if it doesn't exist
        if not self.game_screen:
            self.game_screen = GameScreen(initial_state)
            self.push_screen(self.game_screen)
        else:
            # Update the UI with the initial state
            self.game_screen.update_game_state(initial_state)
        
        # Reset control state for a fresh game
        self.paused = False
        self.last_direction = None
        
        # Double-check snake position to ensure requirement 1.1 is met
        snake_head = initial_state.snake.get_head()
        if snake_head != initial_snake_pos:
            # If snake is not at expected position, recreate it
            self.game_engine.snake = Snake(
                initial_position=initial_snake_pos,
                initial_length=initial_snake_length
            )
            # Place food again to ensure it doesn't overlap with the new snake
            self.game_engine.food.place(self.game_engine.snake)
            # Update the state and UI
            initial_state = self.game_engine.get_state()
            self.game_screen.update_game_state(initial_state)
        
        # Verify food placement is valid (not on snake) to ensure requirement 2.1 is met
        food_pos = initial_state.food.get_position()
        snake_segments = initial_state.snake.get_segments()
        if food_pos in snake_segments:
            # If food overlaps with snake, place it again
            self.game_engine.food.place(self.game_engine.snake)
            # Update the state and UI
            initial_state = self.game_engine.get_state()
            self.game_screen.update_game_state(initial_state)
        
        # Ensure the score display is updated with the initial score of 0
        if self.game_screen:
            self.game_screen.update_game_state(initial_state)
        
        # Log initialization (would be replaced with proper logging in production)
        print("Game initialized with:")
        print(f"- Snake at position: {initial_state.snake.get_head()}")
        print(f"- Food at position: {initial_state.food.get_position()}")
        print(f"- Initial score: {initial_state.score}")
        print(f"- Board dimensions: {self.board_width}x{self.board_height}")
    
    def on_unmount(self) -> None:
        """Clean up resources when the app is unmounted."""
        # Stop the game timer
        self.stop_game_timer()