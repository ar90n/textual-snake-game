# Textual Snake Game

[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
![Built with vibe coding](https://img.shields.io/badge/built%20with-vibe%20coding-ff69b4)

A simple terminal-based Snake Game implemented using the Textual framework.

## Project Structure

The project follows a standard Python package structure:

```
textual-snake-game/
├── src/                           # Source code
│   └── textual_snake_game/        # Main package
│       ├── __init__.py
│       ├── __main__.py            # Module entry point
│       ├── cli.py                 # Command-line interface
│       ├── snake_game.py          # Main game application
│       ├── core/                  # Core game logic
│       │   ├── __init__.py
│       │   ├── models.py          # Data models (Snake, Food)
│       │   └── game_engine.py     # Game engine
│       └── ui/                    # User interface
│           ├── __init__.py
│           └── ui_components.py   # UI components
├── tests/                         # Test files
├── pyproject.toml                 # Project configuration
└── uv.lock                        # Dependency lock file
```

## Features

- Classic snake gameplay in your terminal
- Smooth movement and controls
- Score tracking
- Multiple speed settings
- Pause/resume functionality
- Game over detection for wall and self collisions

## Installation

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the game
uv pip install .
```

### Using pip

```bash
# Install from the current directory
pip install .
```

### Development Setup

```bash
# Using uv (recommended)
uv sync                    # Install all dependencies
uv sync --dev              # Install with dev dependencies (pytest)

# Or using pip
pip install -e .           # Editable install
pip install pytest         # Install test dependencies manually
```

## Running the Game

### Using uv

```bash
# Run directly without installation
uv run textual-snake-game

# Or if you've installed it
textual-snake-game
```

### Using Python

```bash
# Run as a module
python -m textual_snake_game

# Or if installed via pip
textual-snake-game
```

### Command-line Options

```bash
# Show help
textual-snake-game --help

# Set custom board size
textual-snake-game --width 30 --height 20

# Set initial game speed (slow, normal, fast)
textual-snake-game --speed fast
```

## Controls

- **Arrow keys** or **WASD**: Move the snake
- **1/2/3**: Change game speed (slow/normal/fast)
- **P**: Pause/resume game
- **R**: Reset game
- **Q**: Quit game

## Running Tests

### Using uv

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_snake.py

# Run with coverage (if pytest-cov is installed)
uv run pytest --cov=textual_snake_game
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_snake.py
```

## Requirements

- Python 3.13 or higher
- Textual 4.0.0 or higher

## Development

The project uses:
- **uv** for dependency management
- **pytest** for testing
- **Textual** for the terminal UI framework

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything works
5. Submit a pull request