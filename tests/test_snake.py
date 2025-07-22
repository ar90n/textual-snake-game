"""
Unit tests for Snake data model.
"""

import unittest
from src.snake_game.core.models import Snake, DIRECTIONS


class TestSnake(unittest.TestCase):
    """Test cases for Snake class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.snake = Snake(initial_position=(10, 10), initial_length=3)
    
    def test_snake_initialization(self):
        """Test snake initialization with correct position and length."""
        # Check initial segments
        expected_segments = [(10, 10), (9, 10), (8, 10)]
        self.assertEqual(self.snake.get_segments(), expected_segments)
        
        # Check initial direction
        self.assertEqual(self.snake.get_direction(), DIRECTIONS['right'])
        
        # Check initial length
        self.assertEqual(self.snake.get_length(), 3)
    
    def test_get_head(self):
        """Test getting snake head position."""
        self.assertEqual(self.snake.get_head(), (10, 10))
        
        # Move and check head changes
        self.snake.move()
        self.assertEqual(self.snake.get_head(), (11, 10))
    
    def test_basic_movement(self):
        """Test basic snake movement without growth."""
        initial_length = self.snake.get_length()
        
        # Move right (default direction)
        self.snake.move()
        
        # Check head moved right
        self.assertEqual(self.snake.get_head(), (11, 10))
        
        # Check length unchanged
        self.assertEqual(self.snake.get_length(), initial_length)
        
        # Check segments shifted correctly
        expected_segments = [(11, 10), (10, 10), (9, 10)]
        self.assertEqual(self.snake.get_segments(), expected_segments)
    
    def test_direction_change(self):
        """Test changing snake direction."""
        # Change to up direction
        result = self.snake.set_direction(DIRECTIONS['up'])
        self.assertTrue(result)
        self.assertEqual(self.snake.get_direction(), DIRECTIONS['up'])
        
        # Move and verify direction change
        self.snake.move()
        self.assertEqual(self.snake.get_head(), (10, 9))
    
    def test_invalid_direction_change(self):
        """Test prevention of 180-degree direction changes."""
        # Try to change from right to left (opposite direction)
        result = self.snake.set_direction(DIRECTIONS['left'])
        self.assertFalse(result)
        
        # Direction should remain unchanged
        self.assertEqual(self.snake.get_direction(), DIRECTIONS['right'])
        
        # Test other invalid combinations
        self.snake.set_direction(DIRECTIONS['up'])
        result = self.snake.set_direction(DIRECTIONS['down'])
        self.assertFalse(result)
        self.assertEqual(self.snake.get_direction(), DIRECTIONS['up'])
    
    def test_valid_direction_changes(self):
        """Test valid direction changes (90-degree turns)."""
        # From right to up
        result = self.snake.set_direction(DIRECTIONS['up'])
        self.assertTrue(result)
        
        # From up to left
        result = self.snake.set_direction(DIRECTIONS['left'])
        self.assertTrue(result)
        
        # From left to down
        result = self.snake.set_direction(DIRECTIONS['down'])
        self.assertTrue(result)
        
        # From down to right
        result = self.snake.set_direction(DIRECTIONS['right'])
        self.assertTrue(result)
    
    def test_growth(self):
        """Test snake growth functionality."""
        initial_length = self.snake.get_length()
        initial_segments = self.snake.get_segments()
        
        # Grow the snake
        self.snake.grow()
        
        # Check length increased
        self.assertEqual(self.snake.get_length(), initial_length + 1)
        
        # Check head moved but tail remained
        expected_head = (11, 10)  # Moved right from (10, 10)
        self.assertEqual(self.snake.get_head(), expected_head)
        
        # Check all original segments are still there
        new_segments = self.snake.get_segments()
        self.assertEqual(new_segments[1:], initial_segments)
    
    def test_multiple_growth(self):
        """Test multiple consecutive growths."""
        initial_length = self.snake.get_length()
        
        # Grow multiple times
        for i in range(3):
            self.snake.grow()
        
        # Check length increased correctly
        self.assertEqual(self.snake.get_length(), initial_length + 3)
        
        # Check head position after multiple moves
        expected_head = (13, 10)  # Moved right 3 times from (10, 10)
        self.assertEqual(self.snake.get_head(), expected_head)
    
    def test_no_self_collision_initially(self):
        """Test that snake doesn't collide with itself initially."""
        self.assertFalse(self.snake.check_self_collision())
    
    def test_no_self_collision_after_normal_movement(self):
        """Test no self-collision after normal movement."""
        # Move several times
        for _ in range(5):
            self.snake.move()
        
        self.assertFalse(self.snake.check_self_collision())
    
    def test_self_collision_detection(self):
        """Test self-collision detection when snake hits itself."""
        # Create a longer snake
        long_snake = Snake(initial_position=(5, 5), initial_length=5)
        
        # Make snake form a loop to collide with itself
        # Move right, down, left, up to create a square
        long_snake.set_direction(DIRECTIONS['right'])
        long_snake.grow()  # (6, 5)
        
        long_snake.set_direction(DIRECTIONS['down'])
        long_snake.grow()  # (6, 6)
        
        long_snake.set_direction(DIRECTIONS['left'])
        long_snake.grow()  # (5, 6)
        long_snake.grow()  # (4, 6)
        
        long_snake.set_direction(DIRECTIONS['up'])
        long_snake.grow()  # (4, 5)
        
        long_snake.set_direction(DIRECTIONS['right'])
        long_snake.move()  # Should hit body at (5, 5)
        
        self.assertTrue(long_snake.check_self_collision())
    
    def test_growth_with_direction_change(self):
        """Test growth combined with direction changes."""
        # Change direction and grow
        self.snake.set_direction(DIRECTIONS['up'])
        self.snake.grow()
        
        # Check head moved in new direction
        self.assertEqual(self.snake.get_head(), (10, 9))
        
        # Check length increased
        self.assertEqual(self.snake.get_length(), 4)
        
        # Change direction again and grow
        self.snake.set_direction(DIRECTIONS['left'])
        self.snake.grow()
        
        # Check head moved in new direction
        self.assertEqual(self.snake.get_head(), (9, 9))
        
        # Check length increased again
        self.assertEqual(self.snake.get_length(), 5)
    
    def test_segments_immutability(self):
        """Test that get_segments returns a copy, not reference."""
        segments = self.snake.get_segments()
        original_segments = self.snake.get_segments()
        
        # Modify returned segments
        segments.append((0, 0))
        
        # Original should be unchanged
        self.assertEqual(self.snake.get_segments(), original_segments)
        self.assertNotEqual(segments, self.snake.get_segments())


if __name__ == '__main__':
    unittest.main()