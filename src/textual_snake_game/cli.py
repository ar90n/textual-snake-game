"""
Main entry point for the Snake Game application.

This module provides the main entry point for running the Snake Game.
It initializes the game with proper settings and starts the game loop.
"""

import sys
import traceback
import argparse
from typing import Dict, Any

from textual_snake_game.snake_game import SnakeGame


def parse_arguments() -> Dict[str, Any]:
    """Parse command line arguments.
    
    Returns:
        Dictionary of parsed arguments
    """
    parser = argparse.ArgumentParser(description='Snake Game - A simple terminal-based game')
    
    parser.add_argument(
        '--width', 
        type=int, 
        default=20, 
        help='Width of the game board (default: 20)'
    )
    
    parser.add_argument(
        '--height', 
        type=int, 
        default=15, 
        help='Height of the game board (default: 15)'
    )
    
    parser.add_argument(
        '--speed', 
        type=str, 
        choices=['slow', 'normal', 'fast'], 
        default='normal',
        help='Initial game speed (default: normal)'
    )
    
    return vars(parser.parse_args())


def main() -> int:
    """Run the Snake Game.
    
    This function initializes the SnakeGame application with default settings
    and starts the game loop. It ensures proper initialization of:
    - Game board with appropriate dimensions
    - Initial snake placement and length
    - Random food placement
    - Score display starting at 0
    
    Requirements implemented:
    - 1.1: Display snake with initial length on game board
    - 2.1: Place food randomly on the board
    - 3.1: Display initial score of 0
    - 5.4: Use Textual framework for the user interface
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Create the game with specified or default board dimensions
        app = SnakeGame(
            board_width=args['width'],
            board_height=args['height']
        )
        
        # Set initial game speed if specified
        if 'speed' in args:
            app.game_speed = args['speed']
        
        # Display startup message
        print("Starting Snake Game...")
        print(f"Board size: {args['width']}x{args['height']}")
        print(f"Initial speed: {args['speed']}")
        print("Controls:")
        print("  Arrow keys or WASD: Move snake")
        print("  1/2/3: Change speed (slow/normal/fast)")
        print("  P: Pause/resume game")
        print("  R: Reset game")
        print("  Q: Quit game")
        
        # Run the application
        app.run()
        
        return 0  # Success
        
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nGame terminated by user.")
        return 0
        
    except Exception as e:
        # Handle unexpected errors
        print(f"\nError: {str(e)}")
        print("An unexpected error occurred while running the game.")
        traceback.print_exc()
        return 1  # Error


if __name__ == "__main__":
    sys.exit(main())