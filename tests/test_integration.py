"""
Integration tests for the Snake Game.

This module contains integration tests that verify the complete game flow
from start to game over, UI updates with game state changes, and keyboard
input integration with game logic.
"""

import unittest
from unittest.mock import MagicMock, patch

from textual_snake_game.snake_game import SnakeGame
from textual_snake_game.core.game_engine import GameEngine
from textual_snake_game.core.models import DIRECTIONS, Snake, Food, GameState
from textual_snake_game.ui.ui_components import GameScreen, GameBoard, ScoreDisplay


class TestGameIntegration(unittest.TestCase):
    """Integration tests for the Snake Game."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create the snake game
        self.app = SnakeGame(board_width=20, board_height=15)
        
        # Create a real game engine for integration testing
        self.app.game_engine = GameEngine(
            board_width=20,
            board_height=15,
            initial_snake_pos=(10, 7),  # Match the actual center position used in the game
            initial_snake_length=3
        )
        
        # Mock the screen to avoid actual rendering
        self.app.game_screen = MagicMock(spec=GameScreen)
    
    def test_game_initialization(self):
        """Test that the game initializes correctly with all components.
        
        This test verifies requirements:
        - 1.1: Display snake with initial length on game board
        - 2.1: Place food randomly on the board
        - 3.1: Display initial score of 0
        """
        # Call initialize_game to set up the game
        self.app.initialize_game()
        
        # Verify game engine was initialized
        self.assertIsNotNone(self.app.game_engine)
        
        # Verify snake was initialized at the center (requirement 1.1)
        snake_head = self.app.game_engine.snake.get_head()
        expected_head = (10, 7)  # Center of 20x15 board
        self.assertEqual(snake_head, expected_head)
        
        # Verify snake has correct initial length (requirement 1.1)
        self.assertEqual(self.app.game_engine.snake.get_length(), 3)
        
        # Verify food was placed (requirement 2.1)
        self.assertIsNotNone(self.app.game_engine.food.get_position())
        
        # Verify food is not on snake (requirement 2.1)
        snake_segments = self.app.game_engine.snake.get_segments()
        self.assertNotIn(self.app.game_engine.food.get_position(), snake_segments)
        
        # Verify score is 0 (requirement 3.1)
        self.assertEqual(self.app.game_engine.score, 0)
        
        # Verify game is not over
        self.assertFalse(self.app.game_engine.game_over)
        
        # Verify UI was updated with initial state
        self.app.game_screen.update_game_state.assert_called_with(self.app.game_engine.get_state())
    
    def test_complete_game_flow(self):
        """Test the complete game flow from start to game over.
        
        This test verifies requirements:
        - 1.3: Update snake position on board
        - 1.4: Game ends when snake reaches board boundary
        - 2.2: Snake grows when it eats food
        - 2.3: New food placed after consumption
        - 3.2: Score increases when snake eats food
        - 4.1: Game ends when snake hits wall
        """
        # Initialize the game
        self.app.initialize_game()
        
        # Get initial state
        initial_state = self.app.game_engine.get_state()
        initial_score = initial_state.score
        initial_snake_length = initial_state.snake.get_length()
        initial_head = self.app.game_engine.snake.get_head()
        
        # Mock food placement to control the game flow
        # Place food directly in front of the snake
        snake_head = self.app.game_engine.snake.get_head()
        next_pos = (snake_head[0] + 1, snake_head[1])  # Right in front
        self.app.game_engine.food.position = next_pos
        
        # Update game once (snake should move and eat food)
        self.app.update_game()
        
        # Verify snake moved (requirement 1.3)
        new_head = self.app.game_engine.snake.get_head()
        self.assertNotEqual(new_head, initial_head)
        
        # Verify score increased (requirement 3.2)
        self.assertEqual(self.app.game_engine.score, initial_score + 1)
        
        # Verify snake grew (requirement 2.2)
        self.assertEqual(self.app.game_engine.snake.get_length(), initial_snake_length + 1)
        
        # Verify new food was placed (requirement 2.3)
        self.assertIsNotNone(self.app.game_engine.food.get_position())
        self.assertNotEqual(self.app.game_engine.food.get_position(), next_pos)
        
        # Verify UI was updated
        self.app.game_screen.update_game_state.assert_called_with(self.app.game_engine.get_state())
        
        # Reset mock to track new calls
        self.app.game_screen.update_game_state.reset_mock()
        
        # Now force the snake to hit a wall (requirement 1.4, 4.1)
        # Move snake to edge of board
        self.app.game_engine.snake.segments[0] = (19, 10)  # Right at the edge
        
        # Update game (should hit right wall)
        self.app.update_game()
        
        # Verify game is over (requirement 1.4, 4.1)
        self.assertTrue(self.app.game_engine.is_game_over())
        self.assertEqual(self.app.game_engine.get_game_over_reason(), "Wall collision")
        
        # Verify UI was updated with game over state (requirement 4.3)
        self.app.game_screen.update_game_state.assert_called_with(self.app.game_engine.get_state())
    
    def test_keyboard_input_integration(self):
        """Test that keyboard input correctly affects game state.
        
        This test verifies requirements:
        - 1.2: Snake moves in direction of arrow key press
        """
        # Initialize the game
        self.app.initialize_game()
        
        # Get initial direction (should be right)
        initial_direction = self.app.game_engine.snake.get_direction()
        self.assertEqual(initial_direction, DIRECTIONS['right'])
        
        # Test all direction keys
        directions_to_test = ["up", "left", "down", "right"]
        
        for direction in directions_to_test:
            # Create mock key event
            key_event = MagicMock()
            key_event.key = direction
            
            # Send key event
            self.app.on_key(key_event)
            
            # Verify direction changed (except for invalid 180-degree turns)
            new_direction = self.app.game_engine.snake.get_direction()
            
            # Skip validation for 180-degree turns which should be rejected
            if (direction == "down" and initial_direction == DIRECTIONS['up']) or \
               (direction == "up" and initial_direction == DIRECTIONS['down']) or \
               (direction == "left" and initial_direction == DIRECTIONS['right']) or \
               (direction == "right" and initial_direction == DIRECTIONS['left']):
                continue
                
            self.assertEqual(new_direction, DIRECTIONS[direction])
            initial_direction = new_direction
        
        # Test WASD keys as well
        wasd_mapping = {"w": "up", "a": "left", "s": "down", "d": "right"}
        
        for key, direction in wasd_mapping.items():
            # Create mock key event
            key_event = MagicMock()
            key_event.key = key
            
            # Send key event
            self.app.on_key(key_event)
            
            # Verify direction changed (except for invalid 180-degree turns)
            new_direction = self.app.game_engine.snake.get_direction()
            
            # Skip validation for 180-degree turns which should be rejected
            expected_direction = DIRECTIONS[direction]
            if (expected_direction[0] + initial_direction[0] == 0 and 
                expected_direction[1] + initial_direction[1] == 0):
                continue
                
            self.assertEqual(new_direction, DIRECTIONS[direction])
            initial_direction = new_direction
        
        # Test that snake actually moves in the set direction
        # Set direction to up
        up_key_event = MagicMock()
        up_key_event.key = "up"
        self.app.on_key(up_key_event)
        
        # Get head position before update
        head_before = self.app.game_engine.snake.get_head()
        
        # Update game
        self.app.update_game()
        
        # Get head position after update
        head_after = self.app.game_engine.snake.get_head()
        
        # Verify snake moved in the up direction (y decreases)
        self.assertEqual(head_after[0], head_before[0])  # x stays the same
        self.assertEqual(head_after[1], head_before[1] - 1)  # y decreases
    
    def test_ui_updates_with_game_state(self):
        """Test that UI components update correctly with game state changes.
        
        This test verifies requirements:
        - 3.3: Score display updates immediately
        - 5.1: Game board displays clearly
        - 5.2: Snake and food have distinct visual representations
        - 5.3: Score is displayed prominently
        """
        # Initialize the game with a real GameScreen for this test
        self.app.game_engine = GameEngine(
            board_width=20,
            board_height=15,
            initial_snake_pos=(10, 10),
            initial_snake_length=3
        )
        
        # Create a real GameScreen but with mocked widgets
        game_screen = GameScreen(self.app.game_engine.get_state())
        game_screen.game_board = MagicMock(spec=GameBoard)
        game_screen.score_display = MagicMock(spec=ScoreDisplay)
        self.app.game_screen = game_screen
        
        # Update game
        self.app.update_game()
        
        # Verify game board was updated (requirement 5.1, 5.2)
        self.app.game_screen.game_board.update_state.assert_called_once()
        
        # Verify score display was updated (requirement 3.3, 5.3)
        self.app.game_screen.score_display.update_score.assert_called_once()
        
        # Test score updates when snake eats food
        # Reset mocks
        self.app.game_screen.game_board.update_state.reset_mock()
        self.app.game_screen.score_display.update_score.reset_mock()
        
        # Place food where snake will move
        snake_head = self.app.game_engine.snake.get_head()
        next_pos = (snake_head[0] + 1, snake_head[1])  # Right in front
        self.app.game_engine.food.position = next_pos
        
        # Update game (snake should eat food)
        self.app.update_game()
        
        # Verify score display was updated with new score (requirement 3.3)
        self.app.game_screen.score_display.update_score.assert_called_once()
        
        # Verify game board was updated to show new snake position and food (requirement 5.1, 5.2)
        self.app.game_screen.game_board.update_state.assert_called_once()
    
    def test_game_over_detection(self):
        """Test that game over is correctly detected and handled.
        
        This test verifies requirements:
        - 4.1: Game ends when snake hits wall
        - 4.2: Game ends when snake collides with itself
        - 4.3: Game over message is displayed
        - 4.4: Final score is shown
        """
        # Initialize the game
        self.app.initialize_game()
        
        # Force game over conditions
        
        # 1. Wall collision (requirement 4.1)
        self.app.game_engine.snake.segments[0] = (20, 10)  # Outside right wall
        
        # Update game
        self.app.update_game()
        
        # Verify game is over
        self.assertTrue(self.app.game_engine.is_game_over())
        
        # Verify game over reason
        self.assertEqual(self.app.game_engine.get_game_over_reason(), "Wall collision")
        
        # Verify UI was updated with game over state (requirement 4.3, 4.4)
        self.app.game_screen.update_game_state.assert_called_with(self.app.game_engine.get_state())
        
        # Reset game
        self.app.reset_game()
        self.app.game_screen.update_game_state.reset_mock()
        
        # Verify game is not over after reset
        self.assertFalse(self.app.game_engine.is_game_over())
        
        # 2. Self collision (requirement 4.2)
        # Create a snake configuration that will result in self-collision
        self.app.game_engine.snake.segments = [(5, 5), (6, 5), (7, 5), (5, 5)]  # Head at same position as tail
        
        # Update game
        self.app.update_game()
        
        # Verify game is over
        self.assertTrue(self.app.game_engine.is_game_over())
        
        # Verify game over reason
        self.assertEqual(self.app.game_engine.get_game_over_reason(), "Self collision")
        
        # Verify UI was updated with game over state (requirement 4.3, 4.4)
        self.app.game_screen.update_game_state.assert_called_with(self.app.game_engine.get_state())
    
    def test_game_reset(self):
        """Test that game reset works correctly."""
        # Initialize the game
        self.app.initialize_game()
        
        # Change game state
        self.app.game_engine.score = 10
        self.app.game_engine.end_game()
        
        # Reset game
        self.app.reset_game()
        
        # Verify game state was reset
        self.assertEqual(self.app.game_engine.score, 0)
        self.assertFalse(self.app.game_engine.is_game_over())
        
        # Verify snake was reset to initial position and length
        snake_head = self.app.game_engine.snake.get_head()
        expected_head = (10, 7)  # Center of 20x15 board
        self.assertEqual(snake_head, expected_head)
        self.assertEqual(self.app.game_engine.snake.get_length(), 3)
        
        # Verify UI was updated
        self.app.game_screen.update_game_state.assert_called_with(self.app.game_engine.get_state())
    
    def test_pause_functionality(self):
        """Test that pause functionality works correctly."""
        # Initialize the game
        self.app.initialize_game()
        
        # Get initial head position
        initial_head = self.app.game_engine.snake.get_head()
        
        # Pause the game
        self.app.toggle_pause()
        self.assertTrue(self.app.paused)
        
        # Update game (should be skipped due to pause)
        self.app.update_game()
        
        # Verify snake didn't move
        current_head = self.app.game_engine.snake.get_head()
        self.assertEqual(current_head, initial_head)
        
        # Unpause the game
        self.app.toggle_pause()
        self.assertFalse(self.app.paused)
        
        # Update game (should work now)
        self.app.update_game()
        
        # Verify snake moved
        new_head = self.app.game_engine.snake.get_head()
        self.assertNotEqual(new_head, initial_head)
    
    def test_speed_control(self):
        """Test that speed control works correctly."""
        # Initialize the game
        self.app.initialize_game()
        
        # Test changing speeds
        self.app.set_game_speed("slow")
        self.assertEqual(self.app.game_speed, "slow")
        self.assertEqual(self.app.GAME_SPEEDS[self.app.game_speed], 0.3)
        
        self.app.set_game_speed("normal")
        self.assertEqual(self.app.game_speed, "normal")
        self.assertEqual(self.app.GAME_SPEEDS[self.app.game_speed], 0.2)
        
        self.app.set_game_speed("fast")
        self.assertEqual(self.app.game_speed, "fast")
        self.assertEqual(self.app.GAME_SPEEDS[self.app.game_speed], 0.1)
        
        # Test invalid speed
        self.app.set_game_speed("invalid")
        self.assertEqual(self.app.game_speed, "fast")  # Should remain unchanged
    
    def test_snake_growth_mechanics(self):
        """Test that snake grows correctly when eating food.
        
        This test verifies requirements:
        - 2.2: Snake grows by one segment when eating food
        - 2.4: Snake body segments are maintained properly
        """
        # Initialize the game
        self.app.initialize_game()
        
        # Get initial snake length
        initial_length = self.app.game_engine.snake.get_length()
        
        # Get initial segments
        initial_segments = self.app.game_engine.snake.get_segments().copy()
        
        # Place food where snake will move
        snake_head = self.app.game_engine.snake.get_head()
        next_pos = (snake_head[0] + 1, snake_head[1])  # Right in front
        self.app.game_engine.food.position = next_pos
        
        # Update game (snake should eat food)
        self.app.update_game()
        
        # Verify snake grew by exactly one segment (requirement 2.2)
        new_length = self.app.game_engine.snake.get_length()
        self.assertEqual(new_length, initial_length + 1)
        
        # Verify snake body segments are maintained properly (requirement 2.4)
        new_segments = self.app.game_engine.snake.get_segments()
        
        # New head should be at the food position
        self.assertEqual(new_segments[0], next_pos)
        
        # The rest of the segments should match the previous segments
        # (the old tail is kept when growing)
        for i in range(len(initial_segments)):
            self.assertEqual(new_segments[i+1], initial_segments[i])
    
    def test_textual_integration(self):
        """Test integration with Textual framework.
        
        This test verifies requirement:
        - 5.4: Game uses Textual framework for UI
        """
        # Create a new SnakeGame instance
        app = SnakeGame()
        
        # Verify it inherits from Textual's App class
        self.assertTrue(hasattr(app, 'run'))
        self.assertTrue(hasattr(app, 'push_screen'))
        
        # Create a mock GameScreen
        mock_screen = MagicMock(spec=GameScreen)
        app.game_screen = mock_screen
        
        # Create a mock game engine
        app.game_engine = MagicMock(spec=GameEngine)
        app.game_engine.is_game_over.return_value = False
        app.game_engine.get_state.return_value = MagicMock(spec=GameState)
        
        # Set paused to False
        app.paused = False
        
        # Verify the app has the expected components
        self.assertIsNotNone(app.game_screen)
        
        # Test that the app can update the game state
        app.update_game()
        
        # Verify the game engine was updated and the screen was refreshed
        app.game_engine.update.assert_called_once()
        mock_screen.update_game_state.assert_called_once_with(app.game_engine.get_state())
    
    def test_invalid_moves_prevention(self):
        """Test that invalid moves (180-degree turns) are prevented."""
        # Initialize the game
        self.app.initialize_game()
        
        # Set initial direction to right
        self.app.game_engine.snake.direction = DIRECTIONS['right']
        
        # Try to set direction to left (should be prevented)
        left_key_event = MagicMock()
        left_key_event.key = "left"
        self.app.on_key(left_key_event)
        
        # Direction should still be right
        self.assertEqual(self.app.game_engine.snake.get_direction(), DIRECTIONS['right'])
        
        # Set direction to up (should work)
        up_key_event = MagicMock()
        up_key_event.key = "up"
        self.app.on_key(up_key_event)
        
        # Direction should now be up
        self.assertEqual(self.app.game_engine.snake.get_direction(), DIRECTIONS['up'])
        
        # Try to set direction to down (should be prevented)
        down_key_event = MagicMock()
        down_key_event.key = "down"
        self.app.on_key(down_key_event)
        
        # Direction should still be up
        self.assertEqual(self.app.game_engine.snake.get_direction(), DIRECTIONS['up'])
    
    def test_end_to_end_game_flow(self):
        """Test a complete end-to-end game flow with multiple interactions.
        
        This test simulates a complete game from start to finish with:
        - Multiple direction changes
        - Multiple food consumptions
        - Game over condition
        - Score tracking
        """
        # Initialize the game
        self.app.initialize_game()
        
        # Initial score should be 0
        self.assertEqual(self.app.game_engine.score, 0)
        
        # Simulate several moves with food consumption
        for _ in range(3):
            # Place food where snake will move next
            snake_head = self.app.game_engine.snake.get_head()
            direction = self.app.game_engine.snake.get_direction()
            next_pos = (snake_head[0] + direction[0], snake_head[1] + direction[1])
            self.app.game_engine.food.position = next_pos
            
            # Update game (snake should eat food)
            self.app.update_game()
            
            # Change direction (rotate clockwise: right -> down -> left -> up)
            current_direction = self.app.game_engine.snake.get_direction()
            
            if current_direction == DIRECTIONS['right']:
                new_direction = "down"
            elif current_direction == DIRECTIONS['down']:
                new_direction = "left"
            elif current_direction == DIRECTIONS['left']:
                new_direction = "up"
            else:  # up
                new_direction = "right"
                
            key_event = MagicMock()
            key_event.key = new_direction
            self.app.on_key(key_event)
        
        # Verify score increased by 3
        self.assertEqual(self.app.game_engine.score, 3)
        
        # Verify snake length increased by 3
        self.assertEqual(self.app.game_engine.snake.get_length(), 6)  # Initial 3 + 3 food items
        
        # Force game over by wall collision
        self.app.game_engine.snake.segments[0] = (0, 0)  # Place at corner
        self.app.game_engine.snake.direction = DIRECTIONS['left']  # Move towards left wall
        
        # Update game (should hit left wall)
        self.app.update_game()
        
        # Verify game is over
        self.assertTrue(self.app.game_engine.is_game_over())
        self.assertEqual(self.app.game_engine.get_game_over_reason(), "Wall collision")
        
        # Verify final score is preserved
        self.assertEqual(self.app.game_engine.get_final_score(), 3)
        
        # Verify UI was updated with game over state
        self.app.game_screen.update_game_state.assert_called_with(self.app.game_engine.get_state())


if __name__ == '__main__':
    unittest.main()