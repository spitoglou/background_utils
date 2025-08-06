# System Patterns: background-utils

## Architecture
- Single Python package with `src/` layout: `src/background_utils`
- Separation of concerns:
  - CLI: `background_utils.cli` (Typer root app) with command groups under `background_utils.cli.commands`
  - Services: `background_utils.services` (long-running workers/daemons)
  - Sandbox: `background_utils.sandbox` (infinite background processes)
  - Shared: `background_utils.config`, `background_utils.logging`, and future `background_utils.utils`
- Entry points via `pyproject.toml`:
  - `background-utils` → `background_utils.cli.app:main`
  - Combined services with tray:
    - `background-utils-service` → `background_utils.services.manager:main`
  - Individual services:
    - `background-utils-service-example` → `background_utils.services.example_service:main`
    - `background-utils-service-battery` → `background_utils.services.battery_monitor:main`
    - `background-utils-service-my` → `background_utils.services.my_service:main`

## Key Technical Decisions
- Typer for ergonomic CLI with sub-apps per domain (e.g., `example`, `wifi`)
- Rich for user-friendly console output (tables, styling, pretty JSON)
- Loguru for logging with a Rich console sink
- pydantic-settings for configuration via environment variables and `.env`
- Python 3.12+ features and typing (mypy strict mode orientation)

## Command Registration Pattern
- Root CLI initializes logging using a `--verbose` flag:
  - `setup_logging(level="DEBUG" if verbose else "INFO")`
- Subcommands live in `background_utils.cli.commands.<name>` and expose `app: Typer`
- Registered with lazy import and explicit casting for typing:
  - `example_app = cast(Typer, _lazy_import("...example", "app"))`
  - `wifi_app = cast(Typer, _lazy_import("...wifi", "app"))`
  - `app.add_typer(example_app, name="example")`
  - `app.add_typer(wifi_app, name="wifi")`

## Service Pattern
- Cooperative services expose `run(stop_event: threading.Event)` and optionally keep a `main()` for standalone runs.
- `ServiceManager` (manager.py):
  - Starts each service on its own thread
  - Installs signal handlers only when running in the main thread
  - Shares a `stop_event` for graceful shutdown with 10s timeout
  - Continues other services if one crashes (logs exception)
- `TrayController` integrates a Windows system tray icon (pystray + Pillow):
  - Actions: View Log (open Notepad), Stop Services, Restart Services, Exit
  - Ensures tray visibility on startup; hides and force-exits on Exit to avoid ghost icons

## Sandbox Pattern
- `sandbox.py` demonstrates:
  - Infinite loop for continuous monitoring
  - System resource checking (e.g., battery status)
  - Graceful shutdown using `signal` handlers
  - Logging with the project's standard setup

## Wi‑Fi Command (Windows)
- Implemented in `cli/commands/wifi.py`:
  - Uses `netsh` to list profiles and show keys (passwords)
  - Output options: Rich table (default) or JSON (`-o json`)
  - Requires Windows and relevant privileges to read key material
- Future improvement: extract logic to `utils/wifi.py` and add platform guards

## Testing
- Pytest test structure under `tests/`
- Initial smoke tests for module importability
- Next: add Typer CLI invocation tests and service loop tests with shortened intervals

## Logging Pattern
- `background_utils.logging.setup_logging()` sets a Rich console sink for Loguru
- Adds a rotating file sink on Windows at `%LOCALAPPDATA%/background-utils/background-utils.log`
- Consistent structured format; use `logger.info/debug/warning/exception` across code

## Configuration Pattern
- Pydantic v2 model `Settings` in `background_utils.config`
- `.env.example` documents supported variables with prefix `BGU_`
- `load_settings()` to obtain validated runtime configuration

## Cross-Platform Considerations
- Wi‑Fi functionality is currently Windows-only
- Provide helpful messaging on non-Windows platforms
- Scripts for service execution include PowerShell and Bash variants

## Extensibility
- Add new command group:
  1) Create `src/background_utils/cli/commands/<group>.py` with `app: Typer`
  2) Register in `src/background_utils/cli/app.py` using `_lazy_import` and `app.add_typer(...)`
- Add new service:
  1) Create `src/background_utils/services/<name>.py` with `main()`
  2) Optionally add `project.scripts` entry in `pyproject.toml` if exposed to users
- Add new sandbox process:
  1) Create `src/background_utils/<name>.py` with `main()` and infinite loop
  2) Add `project.scripts` entry in `pyproject.toml`