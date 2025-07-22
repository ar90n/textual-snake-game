# Textual Snake Game

A simple terminal-based Snake Game implemented using the Textual framework.

## Project Structure

The project follows a standard Pythonic structure:

```
textual-snake-game/
├── src/                    # Source code
│   ├── cli.py              # Command-line interface
│   └── snake_game/         # Main package
│       ├── core/           # Core game logic
│       │   ├── models.py   # Data models
│       │   └── game_engine.py # Game engine
│       ├── ui/             # User interface
│       │   └── ui_components.py # UI components
│       └── snake_game.py   # Main game class
├── tests/                  # Test files
├── run_game.py             # Executable script to run the game
└── pyproject.toml          # Project configuration
```

## Features

- Classic snake gameplay in your terminal
- Smooth movement and controls
- Score tracking
- Multiple speed settings
- Pause/resume functionality
- Game over detection for wall and self collisions

## Installation

### Using pip

```bash
# Install from the current directory
pip install .
```

### Development Setup

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Running the Game

### As an installed package

```bash
# If installed with pip
snake-game
```

### From the source code

```bash
# Run the executable script
./run_game.py

# Or run as a module
python -m src
```

### Command-line Options

```bash
# Show help
snake-game --help

# Set custom board size
snake-game --width 30 --height 20

# Set initial game speed (slow, normal, fast)
snake-game --speed fast
```

## Controls

- **Arrow keys** or **WASD**: Move the snake
- **1/2/3**: Change game speed (slow/normal/fast)
- **P**: Pause/resume game
- **R**: Reset game
- **Q**: Quit game

## Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests/test_snake.py
```

## Requirements

- Python 3.13 or higher
- Textual 4.0.0 or higher