# background-utils

Personal automation and production tools for Python 3.12+. Includes Typer-based CLIs and long-running services with Pydantic config, Loguru logging, and Rich output.

## Quick start

1) Install (editable):
    pip install -e .[dev]

2) Run CLI:
    background-utils --help

3) Run example service (foreground):
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
  - background-utils-service: example service runner