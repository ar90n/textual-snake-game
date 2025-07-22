"""
UI components for the Snake Game using Textual framework.
"""

from textual.app import App
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Label
from textual.containers import Container
from textual.reactive import reactive
from textual import events
from rich.console import RenderableType
from rich.text import Text
from rich.style import Style
from typing import List, Tuple, Optional

from textual_snake_game.core.models import GameState


class GameBoard(Widget):
    """Widget to render the game board, snake, and food."""

    # Reactive properties that will trigger a refresh when changed
    game_state = reactive(None)

    # Visual characters for different elements
    SNAKE_HEAD = "█"
    SNAKE_BODY = "█"
    FOOD = "●"
    EMPTY = " "
    BORDER_HORIZONTAL = "─"
    BORDER_VERTICAL = "│"
    BORDER_TOP_LEFT = "┌"
    BORDER_TOP_RIGHT = "┐"
    BORDER_BOTTOM_LEFT = "└"
    BORDER_BOTTOM_RIGHT = "┘"

    # Styles for different elements
    SNAKE_HEAD_STYLE = Style(color="bright_green")
    SNAKE_BODY_STYLE = Style(color="green")
    FOOD_STYLE = Style(color="bright_red")
    BORDER_STYLE = Style(color="bright_blue")

    def __init__(self, game_state: Optional[GameState] = None, **kwargs):
        """Initialize the game board widget.

        Args:
            game_state: Initial game state
            **kwargs: Additional widget parameters
        """
        super().__init__(**kwargs)
        self.game_state = game_state

    def update_state(self, new_state: GameState) -> None:
        """Update the game state and refresh the display.

        Args:
            new_state: New game state to display
        """
        self.game_state = new_state
        self.refresh()

    def render(self) -> RenderableType:
        """Render the game board with snake and food.

        Returns:
            Rich renderable for the game board
        """
        if not self.game_state:
            # If no game state, render empty text
            return Text("No game state")

        # Get board dimensions
        width = self.game_state.board_width
        height = self.game_state.board_height

        # Create a 2D grid for the board
        grid = [[self.EMPTY for _ in range(width)] for _ in range(height)]

        # Place snake on the grid
        snake_segments = self.game_state.snake.get_segments()
        for i, segment in enumerate(snake_segments):
            x, y = segment
            # Ensure coordinates are within bounds
            if 0 <= x < width and 0 <= y < height:
                grid[y][x] = self.SNAKE_HEAD if i == 0 else self.SNAKE_BODY

        # Place food on the grid
        food_x, food_y = self.game_state.food.get_position()
        if 0 <= food_x < width and 0 <= food_y < height:
            grid[food_y][food_x] = self.FOOD

        # Build the board as a Text object
        board_text = Text()
        
        # Add title
        title = "SNAKE GAME"
        if self.game_state.game_over:
            title += " - GAME OVER!"
        board_text.append(title.center(width + 2) + "\n", style="bold white")
        
        # Add top border
        board_text.append(self.BORDER_TOP_LEFT, style=self.BORDER_STYLE)
        board_text.append(self.BORDER_HORIZONTAL * width, style=self.BORDER_STYLE)
        board_text.append(self.BORDER_TOP_RIGHT + "\n", style=self.BORDER_STYLE)

        # Add game board rows with side borders
        for row in grid:
            board_text.append(self.BORDER_VERTICAL, style=self.BORDER_STYLE)
            
            for cell in row:
                if cell == self.SNAKE_HEAD:
                    board_text.append(cell, style=self.SNAKE_HEAD_STYLE)
                elif cell == self.SNAKE_BODY:
                    board_text.append(cell, style=self.SNAKE_BODY_STYLE)
                elif cell == self.FOOD:
                    board_text.append(cell, style=self.FOOD_STYLE)
                else:
                    board_text.append(cell)
            
            board_text.append(self.BORDER_VERTICAL + "\n", style=self.BORDER_STYLE)

        # Add bottom border
        board_text.append(self.BORDER_BOTTOM_LEFT, style=self.BORDER_STYLE)
        board_text.append(self.BORDER_HORIZONTAL * width, style=self.BORDER_STYLE)
        board_text.append(self.BORDER_BOTTOM_RIGHT, style=self.BORDER_STYLE)
        
        return board_text


class ScoreDisplay(Widget):
    """Widget to display the current score."""

    # Reactive property for score
    score = reactive(0)

    def __init__(self, initial_score: int = 0, **kwargs):
        """Initialize the score display widget.

        Args:
            initial_score: Starting score value
            **kwargs: Additional widget parameters
        """
        super().__init__(**kwargs)
        self.score = initial_score

    def update_score(self, new_score: int) -> None:
        """Update the displayed score.

        Args:
            new_score: New score value to display
        """
        self.score = new_score
        self.refresh()

    def render(self) -> RenderableType:
        """Render the score display.

        Returns:
            Rich renderable for the score display
        """
        # Create a text with the score prominently displayed
        score_text = Text(f"Score: {self.score}", style="bold white on dark_blue")
        return score_text


class GameScreen(Screen):
    """Main game screen layout combining all game widgets."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reset", "Reset Game"),
        ("p", "pause", "Pause/Resume"),
    ]

    CSS = """
    #game-container {
        width: 100%;
        height: 100%;
        layout: vertical;
        background: #1f1f1f;
        align: center middle;
    }

    #game-board {
        width: 100%;
        height: 1fr;
        min-height: 15;
        margin: 1 2;
        align: center middle;
    }

    #score-display {
        width: 100%;
        height: auto;
        margin: 0 2 1 2;
    }
    
    #header {
        width: 100%;
        height: auto;
        content-align: center middle;
        background: #2d2d2d;
        color: #ffffff;
        padding: 1;
        border-bottom: solid #3d3d3d;
    }
    
    #footer {
        width: 100%;
        height: auto;
        content-align: center middle;
        background: #2d2d2d;
        color: #ffffff;
        padding: 1;
        border-top: solid #3d3d3d;
    }
    
    #title {
        text-style: bold;
        color: white;
    }
    
    #controls {
        text-opacity: 60%;
        color: white;
    }
    """

    def __init__(self, game_state: Optional[GameState] = None):
        """Initialize the game screen.

        Args:
            game_state: Initial game state
        """
        super().__init__()
        self.game_state = game_state
        self.paused = False

    def compose(self):
        """Compose the screen layout with game board and score display.

        Returns:
            Iterable of widgets for the screen
        """
        # Create a vertical layout with header, game board, score, and footer
        with Container(id="game-container"):
            # Header with title
            with Container(id="header"):
                yield Label("SNAKE GAME", id="title")

            # Game board takes most of the space
            self.game_board = GameBoard(self.game_state, id="game-board")
            yield self.game_board

            # Score display
            self.score_display = ScoreDisplay(
                initial_score=self.game_state.score if self.game_state else 0,
                id="score-display",
            )
            yield self.score_display

            # Footer with controls
            with Container(id="footer"):
                yield Label(
                    "Controls: ↑/↓/←/→ - Move | 1/2/3 - Speed | R - Reset | P - Pause | Q - Quit",
                    id="controls",
                )

    def update_game_state(self, new_state: GameState) -> None:
        """Update the game state and refresh all components.

        Args:
            new_state: New game state to display
        """
        self.game_state = new_state
        self.game_board.update_state(new_state)
        self.score_display.update_score(new_state.score)

    def action_reset(self) -> None:
        """Reset the game when 'r' key is pressed."""
        self.app.reset_game()

    def action_pause(self) -> None:
        """Pause or resume the game when 'p' key is pressed."""
        self.paused = not self.paused
        if hasattr(self.app, "toggle_pause"):
            self.app.toggle_pause()

    def action_quit(self) -> None:
        """Quit the application when 'q' key is pressed."""
        self.app.exit()
