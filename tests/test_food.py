"""
Unit tests for Food data model.
"""

import unittest
from unittest.mock import patch
from textual_snake_game.core.models import Food, Snake


class TestFood(unittest.TestCase):
    """Test cases for Food class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.board_width = 20
        self.board_height = 15
        self.food = Food(self.board_width, self.board_height)
        self.snake = Snake(initial_position=(10, 10), initial_length=3)
    
    def test_food_initialization(self):
        """Test food initialization with correct board dimensions."""
        self.assertEqual(self.food.board_width, 20)
        self.assertEqual(self.food.board_height, 15)
        self.assertEqual(self.food.get_position(), (0, 0))  # Default position before placement
    
    def test_get_position(self):
        """Test getting food position."""
        # Set position manually for testing
        self.food.position = (5, 7)
        self.assertEqual(self.food.get_position(), (5, 7))
    
    def test_place_food_not_on_snake(self):
        """Test that food is not placed on snake segments."""
        # Place food
        self.food.place(self.snake)
        
        # Check that food is not on any snake segment
        snake_segments = self.snake.get_segments()
        self.assertNotIn(self.food.get_position(), snake_segments)
    
    def test_place_food_within_bounds(self):
        """Test that food is placed within board boundaries."""
        # Place food
        self.food.place(self.snake)
        
        # Get position
        x, y = self.food.get_position()
        
        # Check within bounds
        self.assertTrue(0 <= x < self.board_width)
        self.assertTrue(0 <= y < self.board_height)
    
    @patch('random.choice')
    def test_place_food_uses_random_position(self, mock_choice):
        """Test that food placement uses random selection."""
        # Mock random.choice to return a specific position
        mock_choice.return_value = (5, 5)
        
        # Place food
        position = self.food.place(self.snake)
        
        # Check that random.choice was called
        mock_choice.assert_called_once()
        
        # Check that the returned position matches the mocked choice
        self.assertEqual(position, (5, 5))
        self.assertEqual(self.food.get_position(), (5, 5))
    
    def test_place_food_handles_full_board(self):
        """Test food placement when board is full (edge case)."""
        # Create a small board
        small_food = Food(3, 1)
        
        # Create a snake that fills the entire board
        small_snake = Snake(initial_position=(2, 0), initial_length=3)
        
        # Place food (should default to 0,0 when no space available)
        position = small_food.place(small_snake)
        
        # Check position
        self.assertEqual(position, (0, 0))
    
    @patch('random.randint')
    def test_place_efficiently(self, mock_randint):
        """Test efficient food placement."""
        # Mock random.randint to return specific positions
        # First call for x, second for y
        mock_randint.side_effect = [5, 8]
        
        # Place food efficiently
        position = self.food.place_efficiently(self.snake)
        
        # Check that random.randint was called twice (once for x, once for y)
        self.assertEqual(mock_randint.call_count, 2)
        
        # Check that the returned position matches the mocked values
        self.assertEqual(position, (5, 8))
        self.assertEqual(self.food.get_position(), (5, 8))
    
    @patch('random.randint')
    def test_place_efficiently_avoids_snake(self, mock_randint):
        """Test that efficient placement avoids snake segments."""
        # Get snake segments
        snake_segments = self.snake.get_segments()
        
        # Mock random.randint to first return a position on the snake,
        # then a valid position not on the snake
        mock_randint.side_effect = [
            snake_segments[0][0], snake_segments[0][1],  # First attempt: on snake
            5, 8  # Second attempt: not on snake
        ]
        
        # Place food efficiently
        position = self.food.place_efficiently(self.snake)
        
        # Check that the returned position is not on the snake
        self.assertNotIn(position, snake_segments)
        self.assertEqual(position, (5, 8))
    
    @patch('random.randint')
    def test_place_efficiently_fallback(self, mock_randint):
        """Test fallback to exhaustive method when efficient method fails."""
        # Mock random.randint to always return a position on the snake
        snake_head = self.snake.get_head()
        mock_randint.return_value = snake_head[0]  # Always return snake head position
        
        # Mock the exhaustive place method
        original_place = self.food.place
        self.food.place = lambda snake: (7, 7)
        
        # Try to place efficiently with a very low max_attempts
        position = self.food.place_efficiently(self.snake, max_attempts=2)
        
        # Check that we got the fallback position
        self.assertEqual(position, (7, 7))
        
        # Restore original place method
        self.food.place = original_place
    
    def test_multiple_placements(self):
        """Test multiple consecutive food placements."""
        # Place food multiple times
        positions = []
        for _ in range(5):
            positions.append(self.food.place(self.snake))
        
        # Check that all positions are valid (not on snake, within bounds)
        snake_segments = self.snake.get_segments()
        for pos in positions:
            x, y = pos
            self.assertNotIn(pos, snake_segments)
            self.assertTrue(0 <= x < self.board_width)
            self.assertTrue(0 <= y < self.board_height)


if __name__ == '__main__':
    unittest.main()