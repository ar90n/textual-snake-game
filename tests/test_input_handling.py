"""
Unit tests for keyboard input handling.
"""

import unittest
from unittest.mock import patch, MagicMock
from textual import events
from textual_snake_game.snake_game import SnakeGame
from textual_snake_game.core.models import DIRECTIONS


class TestInputHandling(unittest.TestCase):
    """Test cases for keyboard input handling."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a mock for the game engine
        self.mock_game_engine = MagicMock()
        self.mock_game_engine.is_game_over.return_value = False
        
        # Create the snake game with mocked engine
        self.app = SnakeGame()
        self.app.game_engine = self.mock_game_engine
    
    def test_arrow_key_detection(self):
        """Test that arrow keys are correctly detected and mapped to directions."""
        # Test up arrow key
        up_key_event = MagicMock()
        up_key_event.key = "up"
        self.app.on_key(up_key_event)
        self.mock_game_engine.set_direction.assert_called_with("up")
        self.mock_game_engine.set_direction.reset_mock()
        
        # Test down arrow key
        down_key_event = MagicMock()
        down_key_event.key = "down"
        self.app.on_key(down_key_event)
        self.mock_game_engine.set_direction.assert_called_with("down")
        self.mock_game_engine.set_direction.reset_mock()
        
        # Test left arrow key
        left_key_event = MagicMock()
        left_key_event.key = "left"
        self.app.on_key(left_key_event)
        self.mock_game_engine.set_direction.assert_called_with("left")
        self.mock_game_engine.set_direction.reset_mock()
        
        # Test right arrow key
        right_key_event = MagicMock()
        right_key_event.key = "right"
        self.app.on_key(right_key_event)
        self.mock_game_engine.set_direction.assert_called_with("right")
    
    def test_wasd_key_detection(self):
        """Test that WASD keys are correctly detected and mapped to directions."""
        # Test W key
        w_key_event = MagicMock()
        w_key_event.key = "w"
        self.app.on_key(w_key_event)
        self.mock_game_engine.set_direction.assert_called_with("up")
        self.mock_game_engine.set_direction.reset_mock()
        
        # Test S key
        s_key_event = MagicMock()
        s_key_event.key = "s"
        self.app.on_key(s_key_event)
        self.mock_game_engine.set_direction.assert_called_with("down")
        self.mock_game_engine.set_direction.reset_mock()
        
        # Test A key
        a_key_event = MagicMock()
        a_key_event.key = "a"
        self.app.on_key(a_key_event)
        self.mock_game_engine.set_direction.assert_called_with("left")
        self.mock_game_engine.set_direction.reset_mock()
        
        # Test D key
        d_key_event = MagicMock()
        d_key_event.key = "d"
        self.app.on_key(d_key_event)
        self.mock_game_engine.set_direction.assert_called_with("right")
    
    def test_invalid_key_ignored(self):
        """Test that invalid keys are ignored."""
        # Reset mock to ensure clean state
        self.mock_game_engine.set_direction.reset_mock()
        
        # Test an invalid key
        invalid_key_event = MagicMock()
        invalid_key_event.key = "x"
        self.app.on_key(invalid_key_event)
        self.mock_game_engine.set_direction.assert_not_called()
    
    def test_input_ignored_when_game_over(self):
        """Test that input is ignored when game is over."""
        # Set game over state
        self.mock_game_engine.is_game_over.return_value = True
        
        # Reset mock to ensure clean state
        self.mock_game_engine.set_direction.reset_mock()
        
        # Test a valid key
        key_event = MagicMock()
        key_event.key = "up"
        self.app.on_key(key_event)
        
        # Direction should not be set
        self.mock_game_engine.set_direction.assert_not_called()
    
    def test_input_ignored_when_paused(self):
        """Test that input is ignored when game is paused."""
        # Set paused state
        self.app.paused = True
        
        # Reset mock to ensure clean state
        self.mock_game_engine.set_direction.reset_mock()
        
        # Test a valid key
        key_event = MagicMock()
        key_event.key = "up"
        self.app.on_key(key_event)
        
        # Direction should not be set
        self.mock_game_engine.set_direction.assert_not_called()
    
    def test_input_validation_prevents_invalid_moves(self):
        """Test that input validation prevents invalid moves."""
        # Mock the set_direction method to return False (invalid move)
        self.mock_game_engine.set_direction.return_value = False
        
        # Test a key that would result in an invalid move
        key_event = MagicMock()
        key_event.key = "up"
        self.app.on_key(key_event)
        
        # Direction should be attempted to be set
        self.mock_game_engine.set_direction.assert_called_with("up")
        
        # The game engine's set_direction method should handle the validation
        # Verify that last_direction is not updated for invalid moves
        self.assertIsNone(self.app.last_direction)


if __name__ == '__main__':
    unittest.main()