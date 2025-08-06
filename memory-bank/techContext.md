# Tech Context: background-utils

## Languages and Runtime
- Python 3.12+ (CPython)

## Core Libraries
- Typer (CLI)
- Rich (terminal output: tables, styling, pretty JSON)
- Pydantic v2 + pydantic-settings (configuration via .env and environment variables)
- Loguru (logging with Rich console sink + rotating file sink on Windows)
- psutil (system and process utilities)
- pystray (Windows system tray integration)
- Pillow (icon image generation for tray)

## Dev Tooling
- Pytest + pytest-cov (tests and coverage)
- Ruff (linting)
- Mypy (type checking, strict configuration)
- Editable install via setuptools with `src/` layout

## Project Layout
- Package root: `src/background_utils`
  - `cli/` Typer root app and command groups
  - `services/` long-running workers/daemons
  - `sandbox.py` infinite background processes
  - `config.py` application configuration
  - `logging.py` logging setup
  - `__init__.py` package init
- Scripts: helper launchers for services (PowerShell and Bash)
- Tests: `tests/` for pytest

## Entry Points (pyproject.toml)
- `background-utils` → `background_utils.cli.app:main`
- Combined services with tray:
  - `background-utils-service` → `background_utils.services.manager:main`
- Individual services:
  - `background-utils-service-example` → `background_utils.services.example_service:main`
  - `background-utils-service-battery` → `background_utils.services.battery_monitor:main`
  - `background-utils-service-my` → `background_utils.services.my_service:main`

## Configuration
- `Settings` model in `background_utils.config`
- `.env.example` documents supported variables with prefix `BGU_`
- Variables: `BGU_LOG_LEVEL`, `BGU_SERVICE_INTERVAL_SECONDS`, `BGU_ENVIRONMENT`, optional `BGU_SENTRY_DSN`
- `load_settings()` loads validated configuration

## Logging
- `setup_logging(level)` configures Loguru with:
  - Rich Console sink (legacy_windows=True for Windows compatibility)
  - Rotating file sink on Windows at `%LOCALAPPDATA%/background-utils/background-utils.log`
- Single initialization at CLI callback / service boot

## Platform Notes
- Wi‑Fi command uses `netsh` (Windows-only); requires privileges to reveal passwords
- Windows tray icon uses `pystray`; when running via `pythonw.exe`, explicit visibility toggling and process termination on Exit are implemented to avoid ghost icons
- Scripts provided for both Windows (PowerShell) and POSIX shells

## Constraints and Considerations
- Keep commands modular under `cli/commands/`
- Prefer strict typing (mypy), clear boundaries, and testable logic
- Provide JSON output options where meaningful for automation

## Installation
- `pip install -e .[dev]` for development environment