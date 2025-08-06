# Progress: background-utils

## What works
- Editable install with dependencies and developer tooling
- Typer-based CLI entry `background-utils`
- CLI command groups:
  - `example` with `hello`, `time`
  - `wifi` with `show-passwords`, `list-networks` (Windows-only), Rich table or JSON output
- **FULLY FUNCTIONAL** Combined services manager with Windows tray icon (pystray + Pillow):
  - Starts services concurrently on dedicated threads
  - **WORKING RELIABLY**: Tray menu: View Log, Stop Services, Restart Services, Exit
  - **FIXED**: All menu operations work without blocking the tray icon
  - **FIXED**: Services actually stop/restart when requested from tray menu
  - **FIXED**: Ctrl+C properly stops services and exits application
  - Graceful shutdown with shared stop_event and 10s timeout
  - **RESOLVED**: Threading conflicts that prevented menu operations
- Individual service runners:
  - `background-utils-service-example`, `background-utils-service-battery`, `background-utils-service-my`
- Windows file logging at `%LOCALAPPDATA%/background-utils/background-utils.log` (rotating)
- Shared configuration via pydantic-settings with `.env` support
- Centralized logging via Loguru with Rich sink
- Helper scripts for service launch (PowerShell/Bash)
- Initial smoke tests validating importability
- Memory Bank moved to root `memory-bank/` and rules updated to reference it

## What's left to build
- Test suite expansion:
  - CLI invocation tests (Typer runner, output capture and exit codes)
  - Service loop tests with shortened intervals and graceful shutdown verification
  - Sandbox process tests for continuous monitoring
- CI workflow (e.g., GitHub Actions): run ruff, mypy, pytest with coverage
- Extract Wi‑Fi logic into `src/background_utils/utils/wifi.py` for reuse and better testability
- Platform guards and graceful messages for non-Windows environments
- Documentation enhancements: usage, troubleshooting, contribution guide

## Current status
- **MILESTONE ACHIEVED**: Foundation complete and fully operational
- **MILESTONE ACHIEVED**: Combined manager with reliable Windows 11 tray integration
- **MILESTONE ACHIEVED**: All tray menu operations working correctly
- Wi‑Fi utilities and sandbox present
- Ready for iterative improvements in tests, CI, and documentation

## Known issues / considerations
- Wi‑Fi command relies on `netsh` and may require admin privileges; permission errors should be handled
- Platform-specific commands need guards or alternative implementations

## Technical Achievements
- **Solved Windows 11 tray compatibility**: Replaced native Win32 implementation with robust pystray solution
- **Resolved threading conflicts**: Fixed manager reference issues that caused silent thread failures
- **Established reliable threading model**: pystray in daemon thread, background workers for menu operations
- **Proven service lifecycle management**: Stop/restart operations work correctly with proper synchronization

## Next milestones
1) Add CLI tests and coverage reporting
2) Introduce CI workflow (lint, type-check, tests)
3) Extract Wi‑Fi logic to `utils/` and add platform checks
4) Expand README with detailed command usage and troubleshooting
5) Add more sandbox processes for system monitoring