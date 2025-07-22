"""
Unit tests for GameEngine class.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.snake_game.core.game_engine import GameEngine
from src.snake_game.core.models import DIRECTIONS, Snake, Food


class TestGameEngine(unittest.TestCase):
    """Test cases for GameEngine class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.engine = GameEngine(board_width=20, board_height=15)
    
    def test_initialization(self):
        """Test game engine initialization."""
        # Check board dimensions
        self.assertEqual(self.engine.board_width, 20)
        self.assertEqual(self.engine.board_height, 15)
        
        # Check initial score and game state
        self.assertEqual(self.engine.score, 0)
        self.assertFalse(self.engine.game_over)
        
        # Check snake initialization
        self.assertIsNotNone(self.engine.snake)
        
        # Check food initialization
        self.assertIsNotNone(self.engine.food)
        
        # Check that food is not on snake
        snake_segments = self.engine.snake.get_segments()
        self.assertNotIn(self.engine.food.get_position(), snake_segments)
    
    def test_get_state(self):
        """Test getting game state."""
        state = self.engine.get_state()
        
        # Check state properties
        self.assertEqual(state.snake, self.engine.snake)
        self.assertEqual(state.food, self.engine.food)
        self.assertEqual(state.score, self.engine.score)
        self.assertEqual(state.game_over, self.engine.game_over)
        self.assertEqual(state.board_width, self.engine.board_width)
        self.assertEqual(state.board_height, self.engine.board_height)
    
    def test_set_direction(self):
        """Test setting snake direction."""
        # Valid direction
        result = self.engine.set_direction('up')
        self.assertTrue(result)
        self.assertEqual(self.engine.snake.get_direction(), DIRECTIONS['up'])
        
        # Invalid direction string
        result = self.engine.set_direction('invalid')
        self.assertFalse(result)
        
        # Invalid direction (opposite)
        self.engine.set_direction('up')
        result = self.engine.set_direction('down')
        self.assertFalse(result)
        self.assertEqual(self.engine.snake.get_direction(), DIRECTIONS['up'])
    
    def test_check_wall_collision(self):
        """Test wall collision detection."""
        # No collision initially
        self.assertFalse(self.engine.check_wall_collision())
        
        # Force snake head position to be outside boundaries
        # Left wall
        self.engine.snake.segments[0] = (-1, 10)
        self.assertTrue(self.engine.check_wall_collision())
        
        # Right wall
        self.engine.snake.segments[0] = (20, 10)
        self.assertTrue(self.engine.check_wall_collision())
        
        # Top wall
        self.engine.snake.segments[0] = (10, -1)
        self.assertTrue(self.engine.check_wall_collision())
        
        # Bottom wall
        self.engine.snake.segments[0] = (10, 15)
        self.assertTrue(self.engine.check_wall_collision())
        
        # No collision when inside boundaries
        self.engine.snake.segments[0] = (10, 10)
        self.assertFalse(self.engine.check_wall_collision())
    
    def test_check_food_collision(self):
        """Test food collision detection."""
        # Initially no collision
        self.assertFalse(self.engine.check_food_collision())
        
        # Force food to be at snake head position
        snake_head = self.engine.snake.get_head()
        self.engine.food.position = snake_head
        
        # Should detect collision
        self.assertTrue(self.engine.check_food_collision())
    
    def test_check_collisions(self):
        """Test combined collision detection."""
        # Initially no collisions
        wall, self_collision, food = self.engine.check_collisions()
        self.assertFalse(wall)
        self.assertFalse(self_collision)
        self.assertFalse(food)
        
        # Test wall collision
        self.engine.snake.segments[0] = (-1, 10)
        wall, self_collision, food = self.engine.check_collisions()
        self.assertTrue(wall)
        self.assertFalse(self_collision)
        self.assertFalse(food)
        
        # Test self collision
        self.engine.snake.segments[0] = (10, 10)
        self.engine.snake.segments[1] = (11, 10)
        self.engine.snake.segments[2] = (10, 10)  # Head collides with tail
        wall, self_collision, food = self.engine.check_collisions()
        self.assertFalse(wall)
        self.assertTrue(self_collision)
        self.assertFalse(food)
        
        # Test food collision
        self.engine.snake.segments[0] = (10, 10)
        self.engine.snake.segments[1] = (9, 10)
        self.engine.snake.segments[2] = (8, 10)
        self.engine.food.position = (10, 10)
        wall, self_collision, food = self.engine.check_collisions()
        self.assertFalse(wall)
        self.assertFalse(self_collision)
        self.assertTrue(food)
    
    def test_update_normal_movement(self):
        """Test normal update with no collisions."""
        # Get initial head position
        initial_head = self.engine.snake.get_head()
        
        # Update game
        result = self.engine.update()
        
        # Game should continue
        self.assertTrue(result)
        self.assertFalse(self.engine.game_over)
        
        # Snake should have moved
        new_head = self.engine.snake.get_head()
        self.assertNotEqual(initial_head, new_head)
        
        # Direction is right by default, so x should increase by 1
        self.assertEqual(new_head[0], initial_head[0] + 1)
        self.assertEqual(new_head[1], initial_head[1])
    
    def test_update_with_food_collision(self):
        """Test update with food collision."""
        # Create a new engine for this test to ensure clean state
        test_engine = GameEngine(board_width=20, board_height=15)
        
        # Get initial state
        initial_length = test_engine.snake.get_length()
        initial_head = test_engine.snake.get_head()
        
        # Place food exactly where the snake's head will move to
        # Snake starts moving right, so food should be at (head_x + 1, head_y)
        next_pos = (initial_head[0] + 1, initial_head[1])
        test_engine.food.position = next_pos
        
        # Verify food is where we expect
        self.assertEqual(test_engine.food.get_position(), next_pos)
        
        # Create a mock for the Food.place method
        mock_place = MagicMock(return_value=(15, 15))
        
        # Save the original method
        original_place = test_engine.food.place
        
        try:
            # Replace with our mock
            test_engine.food.place = mock_place
            
            # Update game
            result = test_engine.update()
            
            # Game should continue
            self.assertTrue(result)
            self.assertFalse(test_engine.game_over)
            
            # Snake should have grown
            new_length = test_engine.snake.get_length()
            self.assertEqual(new_length, initial_length + 1)
            
            # Score should have increased
            self.assertEqual(test_engine.score, 1)
            
            # Verify our mock was called
            mock_place.assert_called_once_with(test_engine.snake)
            
            # Set the food position to what our mock returned
            test_engine.food.position = (15, 15)
            
            # Food should have been placed at new position
            self.assertEqual(test_engine.food.get_position(), (15, 15))
        finally:
            # Restore the original method
            test_engine.food.place = original_place
    
    def test_update_with_wall_collision(self):
        """Test update with wall collision."""
        # Move snake to edge of board
        self.engine.snake.segments[0] = (19, 10)  # Right at the edge
        
        # Update game (should hit right wall)
        result = self.engine.update()
        
        # Game should be over
        self.assertFalse(result)
        self.assertTrue(self.engine.game_over)
    
    def test_update_with_self_collision(self):
        """Test update with self collision."""
        # Create a new engine for this test to ensure clean state
        test_engine = GameEngine(board_width=20, board_height=15)
        
        # Create a snake configuration that will result in self-collision
        # The snake is positioned so that its head will move into its body
        test_engine.snake.segments = [(5, 5), (6, 5), (7, 5), (7, 6), (6, 6), (5, 6)]
        test_engine.snake.direction = DIRECTIONS['up']  # Moving up
        
        # Verify initial state - no collision yet
        self.assertFalse(test_engine.snake.check_self_collision())
        
        # Move the snake up - head will now be at (5, 4)
        test_engine.snake.move()
        
        # Force the head to collide with body
        test_engine.snake.segments[0] = (6, 6)  # This position is part of the snake's body
        
        # Now check for collision
        self.assertTrue(test_engine.snake.check_self_collision())
        
        # Update game state - should detect collision and end game
        result = test_engine.update()
        
        # Game should be over
        self.assertFalse(result)
        self.assertTrue(test_engine.game_over)
    
    def test_update_when_game_already_over(self):
        """Test update when game is already over."""
        # Set game over
        self.engine.game_over = True
        
        # Update should return False
        result = self.engine.update()
        self.assertFalse(result)
    
    def test_reset(self):
        """Test game reset."""
        # Change game state
        self.engine.score = 10
        self.engine.game_over = True
        
        # Reset game
        self.engine.reset()
        
        # Check state was reset
        self.assertEqual(self.engine.score, 0)
        self.assertFalse(self.engine.game_over)
        
        # Check snake and food were reinitialized
        self.assertIsNotNone(self.engine.snake)
        self.assertIsNotNone(self.engine.food)
    
    def test_get_score(self):
        """Test getting the current score."""
        # Initial score should be 0
        self.assertEqual(self.engine.get_score(), 0)
        
        # Set score and check getter
        self.engine.score = 5
        self.assertEqual(self.engine.get_score(), 5)
    
    def test_add_score(self):
        """Test adding points to the score."""
        # Initial score should be 0
        self.assertEqual(self.engine.get_score(), 0)
        
        # Add default points (1)
        new_score = self.engine.add_score()
        self.assertEqual(new_score, 1)
        self.assertEqual(self.engine.get_score(), 1)
        
        # Add specific number of points
        new_score = self.engine.add_score(5)
        self.assertEqual(new_score, 6)
        self.assertEqual(self.engine.get_score(), 6)
    
    def test_score_increases_with_food(self):
        """Test that score increases when snake eats food."""
        # Create a new engine for this test
        test_engine = GameEngine(board_width=20, board_height=15)
        
        # Initial score should be 0
        self.assertEqual(test_engine.get_score(), 0)
        
        # Place food where snake will move
        snake_head = test_engine.snake.get_head()
        next_pos = (snake_head[0] + 1, snake_head[1])  # Right in front
        test_engine.food.position = next_pos
        
        # Mock food placement to avoid randomness
        with patch.object(test_engine.food, 'place', return_value=(15, 15)):
            # Update game (snake should eat food)
            test_engine.update()
            
            # Score should increase by 1
            self.assertEqual(test_engine.get_score(), 1)
            
            # Update again without food collision
            test_engine.update()
            
            # Score should remain the same
            self.assertEqual(test_engine.get_score(), 1)
            
            # Place food in path again
            snake_head = test_engine.snake.get_head()
            next_pos = (snake_head[0] + 1, snake_head[1])
            test_engine.food.position = next_pos
            
            # Update game (snake should eat food again)
            test_engine.update()
            
            # Score should increase to 2
            self.assertEqual(test_engine.get_score(), 2)
    
    def test_is_game_over(self):
        """Test checking if game is over."""
        # Initially game should not be over
        self.assertFalse(self.engine.is_game_over())
        
        # Set game over flag
        self.engine.game_over = True
        
        # Now game should be over
        self.assertTrue(self.engine.is_game_over())
    
    def test_end_game(self):
        """Test manually ending the game."""
        # Initially game should not be over
        self.assertFalse(self.engine.is_game_over())
        
        # End game
        self.engine.end_game()
        
        # Game should be over
        self.assertTrue(self.engine.is_game_over())
        
        # Further updates should return False
        self.assertFalse(self.engine.update())
    
    def test_get_final_score(self):
        """Test getting final score."""
        # Set a score
        self.engine.score = 10
        
        # Get final score
        final_score = self.engine.get_final_score()
        
        # Should match current score
        self.assertEqual(final_score, 10)
        
        # End game and check again
        self.engine.end_game()
        final_score = self.engine.get_final_score()
        self.assertEqual(final_score, 10)
    
    def test_game_over_reason_wall_collision(self):
        """Test getting game over reason for wall collision."""
        # Force snake head position to be outside boundaries
        self.engine.snake.segments[0] = (-1, 10)
        
        # End game
        self.engine.end_game()
        
        # Check reason
        reason = self.engine.get_game_over_reason()
        self.assertEqual(reason, "Wall collision")
    
    def test_game_over_reason_self_collision(self):
        """Test getting game over reason for self collision."""
        # Force snake to collide with itself
        self.engine.snake.segments = [(5, 5), (6, 5), (7, 5), (5, 5)]  # Head at same position as tail
        
        # End game
        self.engine.end_game()
        
        # Check reason
        reason = self.engine.get_game_over_reason()
        self.assertEqual(reason, "Self collision")
    
    def test_game_over_reason_manual_end(self):
        """Test getting game over reason for manual end."""
        # End game without any collision
        self.engine.end_game()
        
        # Check reason
        reason = self.engine.get_game_over_reason()
        self.assertEqual(reason, "Game ended")
    
    def test_game_over_reason_when_game_not_over(self):
        """Test getting game over reason when game is not over."""
        # Game not over yet
        reason = self.engine.get_game_over_reason()
        self.assertEqual(reason, "")


if __name__ == '__main__':
    unittest.main()