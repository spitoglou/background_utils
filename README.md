# background-utils

Personal automation and production tools for Python 3.12+. Includes Typer-based CLIs and long-running services with Pydantic config, Loguru logging, and Rich output.

## Quick start

1) Install (editable):
    pip install -e .[dev]

2) Run CLI:
    background-utils --help

3) Run services with system tray (Windows):
    background-utils-service

## Project structure

- src/background_utils: package code
  - cli: Typer app and commands
  - services: long-running workers/daemons
  - utils: shared helpers
  - config.py: settings via pydantic-settings
  - logging.py: loguru configuration
- scripts: helpers for service process management
- tests: pytest tests

## Services and System Tray (Windows)

The main service entry point `background-utils-service` launches a system tray icon that manages long-running services:

- **Tray Menu Options:**
  - **View Log**: Opens the log file in Notepad (%LOCALAPPDATA%\background-utils\background-utils.log)
  - **Stop Services**: Gracefully stops all running services
  - **Restart Services**: Stops current services and starts fresh instances
  - **Exit**: Stops services and exits the application

- **Service Management:**
  - Services run on dedicated threads with cooperative shutdown via shared stop_event
  - Graceful shutdown with 10-second timeout for each service
  - Individual service entry points available for testing:
    - background-utils-service-example
    - background-utils-service-battery
    - background-utils-service-my

- **Windows Compatibility:**
  - Fully functional on Windows 11 with reliable tray icon behavior
  - No ghost icons - proper cleanup on exit
  - Responsive tray menu with non-blocking operations
  - Ctrl+C support for console-based shutdown

## Development

- Python 3.12+
- Tooling: ruff, mypy, pytest

Common commands:

- Lint:
    ruff check .
- Type-check:
    mypy .
- Tests:
    pytest

## Packaging

- pyproject.toml uses setuptools with package discovery under src/.
- Entry points:
  - background-utils: CLI
  - background-utils-service: combined service manager with system tray

## Development Tools

This project's development was facilitated by AI code assisting tools including:

- **Claude Code**: Interactive CLI development environment
- **Claude Sonnet Models**: Code generation and architectural guidance
- **Kilo Code**: Development assistance and code optimization
- **Qwen3 Code Models**: Code analysis and improvement suggestions
- **Kimi2 Models**: Development workflow automation

These AI tools helped accelerate development, improve code quality, and provide architectural insights throughout the project lifecycle.
