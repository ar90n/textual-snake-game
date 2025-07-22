"""
Unit tests for game timer and update loop.
"""

import unittest
from unittest.mock import patch, MagicMock, call
from textual_snake_game.snake_game import SnakeGame
from textual_snake_game.core.models import GameState, Snake, Food


class TestGameTimer(unittest.TestCase):
    """Test cases for game timer and update loop."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a mock for the game engine
        self.mock_game_engine = MagicMock()
        self.mock_game_engine.is_game_over.return_value = False
        
        # Create mock game state
        self.mock_state = MagicMock(spec=GameState)
        self.mock_game_engine.get_state.return_value = self.mock_state
        
        # Create the snake game with mocked engine
        self.app = SnakeGame()
        self.app.game_engine = self.mock_game_engine
        
        # Mock the game screen
        self.app.game_screen = MagicMock()
    
    def test_update_game_calls_engine_update(self):
        """Test that update_game calls the game engine's update method."""
        # Call the update_game method
        self.app.update_game()
        
        # Verify that the game engine's update method was called
        self.mock_game_engine.update.assert_called_once()
    
    def test_update_game_updates_ui(self):
        """Test that update_game updates the UI with the new game state."""
        # Call the update_game method
        self.app.update_game()
        
        # Verify that the game screen's update_game_state method was called with the game state
        self.app.game_screen.update_game_state.assert_called_once_with(self.mock_state)
    
    def test_update_game_skipped_when_paused(self):
        """Test that update_game is skipped when the game is paused."""
        # Set paused state
        self.app.paused = True
        
        # Call the update_game method
        self.app.update_game()
        
        # Verify that the game engine's update method was not called
        self.mock_game_engine.update.assert_not_called()
        
        # Verify that the game screen's update_game_state method was not called
        self.app.game_screen.update_game_state.assert_not_called()
    
    def test_update_game_skipped_when_game_over(self):
        """Test that update_game is skipped when the game is over."""
        # Set game over state
        self.mock_game_engine.is_game_over.return_value = True
        
        # Call the update_game method
        self.app.update_game()
        
        # Verify that the game engine's update method was not called
        self.mock_game_engine.update.assert_not_called()
        
        # Verify that the game screen's update_game_state method was not called
        self.app.game_screen.update_game_state.assert_not_called()
    
    def test_game_timer_setup(self):
        """Test that the game timer is set up correctly."""
        # Create a new SnakeGame instance with mocked start_game_timer
        app = SnakeGame()
        app.start_game_timer = MagicMock()
        
        # Call _setup_game_timer directly
        app._setup_game_timer()
        
        # Verify that start_game_timer was called with the correct interval
        app.start_game_timer.assert_called_once()
        args = app.start_game_timer.call_args[0]
        self.assertEqual(len(args), 1)
        self.assertIsInstance(args[0], float)  # First arg should be a float (interval)
        self.assertEqual(args[0], app.GAME_SPEEDS[app.game_speed])  # Should use the game speed interval
    
    def test_game_speed_adjustment(self):
        """Test that the game speed can be adjusted."""
        # Initial speed should be moderate
        self.assertEqual(self.app.game_speed, "normal")
        
        # Change to fast speed
        self.app.set_game_speed("fast")
        self.assertEqual(self.app.game_speed, "fast")
        
        # Change to slow speed
        self.app.set_game_speed("slow")
        self.assertEqual(self.app.game_speed, "slow")
        
        # Invalid speed should be ignored
        self.app.set_game_speed("invalid")
        self.assertEqual(self.app.game_speed, "slow")  # Should remain unchanged
    
    @patch('textual_snake_game.snake_game.SnakeGame._setup_game_timer')
    def test_timer_reset_on_speed_change(self, mock_setup_game_timer):
        """Test that the timer is reset when the game speed changes."""
        # Setup
        app = SnakeGame()
        app.game_timer = MagicMock()  # Mock timer object
        
        # Change speed
        app.set_game_speed("fast")
        
        # Verify that _setup_game_timer was called to reset the timer
        mock_setup_game_timer.assert_called_once()
    
    def test_key_changes_game_speed(self):
        """Test that pressing number keys changes the game speed."""
        # Mock key events
        mock_event1 = MagicMock()
        mock_event1.key = "1"
        
        mock_event2 = MagicMock()
        mock_event2.key = "2"
        
        mock_event3 = MagicMock()
        mock_event3.key = "3"
        
        # Test slow speed (1)
        self.app.on_key(mock_event1)
        self.assertEqual(self.app.game_speed, "slow")
        
        # Test normal speed (2)
        self.app.on_key(mock_event2)
        self.assertEqual(self.app.game_speed, "normal")
        
        # Test fast speed (3)
        self.app.on_key(mock_event3)
        self.assertEqual(self.app.game_speed, "fast")


if __name__ == '__main__':
    unittest.main()