# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Install dependencies (editable):**
```bash
pip install -e .[dev]
```

**Code quality checks:**
```bash
ruff check .          # Lint code
mypy .                # Type checking  
pytest                # Run tests
```

**Run the CLI:**
```bash
background-utils --help
background-utils example hello
background-utils wifi show-passwords
background-utils wifi list-networks
```

**Run services:**
```bash
# Combined service manager with Windows system tray
background-utils-service

# Individual services for testing
background-utils-service-example
background-utils-service-battery
background-utils-service-my
```

## Architecture Overview

This is a Python package for personal automation tools with two main components:

### 1. CLI Application (`src/background_utils/cli/`)
- **Typer-based CLI** with lazy-loaded subcommands in `cli/commands/`
- Main app in `cli/app.py` with auto-discovery of command modules
- Commands are organized as separate Typer apps (example, wifi)

### 2. Service Management (`src/background_utils/services/`)
- **ServiceManager**: Thread-based service orchestration with cooperative shutdown
- **TrayController**: Windows system tray integration using pystray
- Individual services implement `run(stop_event: threading.Event) -> None`
- Services are collected in `manager.py:_collect_default_services()`

### Core Infrastructure
- **Configuration**: Pydantic Settings with environment variable support (`BGU_` prefix)
- **Logging**: Loguru with Rich console output + file logging to `%LOCALAPPDATA%\background-utils\`
- **Windows Integration**: Native tray icon, Notepad log viewer, proper shutdown handling

## Key Design Patterns

**Service Pattern:**
```python
def run(stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        # Do work
        time.sleep(interval)
```

**Adding New Services:**
1. Create service module in `services/` with `run()` function
2. Add entry point in `pyproject.toml`
3. Import and add to `_collect_default_services()` in `manager.py`

**Adding CLI Commands:**
1. Create command module in `cli/commands/` with Typer app
2. Import and register in `cli/app.py`

**Configuration Management:**
- Settings loaded from environment variables with `BGU_` prefix
- Pydantic validation with sensible defaults
- `.env` file support for local development

## Windows-Specific Features

- **System Tray**: pystray-based with context menu (View Log, Stop/Restart Services, Exit)
- **Log Access**: Tray menu opens logs in Notepad from `%LOCALAPPDATA%\background-utils\`
- **Process Management**: Handles Windows threading limitations for signal handlers
- **Graceful Shutdown**: 10-second timeout per service with proper cleanup