# Active Context: background-utils

## Current Focus

- Foundation scaffold for CLIs, services, and sandbox processes is in place
- Integrated Wi‑Fi utilities (Windows)
- **COMPLETED**: Robust Windows tray icon implementation working reliably on Windows 11
- **COMPLETED**: Gmail notification service with desktop alerts and persistent UID tracking
- **COMPLETED**: Comprehensive CLAUDE.md file created for future Claude Code instances
- Next: expand tests/CI and documentation

## Recent Changes

- Established src-layout Python 3.12+ package with Typer CLI and example service
- Implemented shared logging (Loguru + Rich) and configuration (pydantic-settings)
- Added CLI command groups:
  - example (hello, time)
  - wifi (show-passwords, list-networks) — Windows-only via `netsh`, table/JSON output
- **IMPROVED**: Wi-Fi command error handling with privilege detection and cleaner messaging
- **MAJOR FIX**: Completely rewrote tray implementation for Windows 11 compatibility:
  - Removed problematic native Win32 tray code that had menu callback issues
  - Implemented clean pystray-only solution with proper threading model
  - Fixed critical threading conflict where `_ensure_manager()` was creating new managers during operations
  - All tray menu functions now work reliably: Stop Services, Restart Services, Exit, View Log
  - Tray remains responsive after operations and Ctrl+C works properly
- **MAJOR ADDITION**: Gmail notification service implementation:
  - IMAP over SSL connection to Gmail (`imap.gmail.com:993`)
  - UID-based email tracking with persistent cache (`%LOCALAPPDATA%\background-utils\gmail_last_uid.txt`)
  - Cross-platform notifications using `plyer` + `win10toast` fallback
  - 60-second check interval with cooperative threading
  - Configuration via `BGU_GMAIL_EMAIL` and `BGU_GMAIL_PASSWORD`
  - Fixed duplicate notification issue with explicit UID filtering
  - Automatic reconnection on connection errors
- Combined service manager:
  - Threads for: example_service, battery_monitor, gmail_notifier, my_service
  - Windows tray integration (pystray + Pillow) providing View Log, Stop Services, Restart Services, Exit
  - Logging writes to %LOCALAPPDATA%/background-utils/background-utils.log (rotating)
- Updated entry points:
  - Combined: background-utils-service → services.manager:main
  - Individual: background-utils-service-example, background-utils-service-battery, background-utils-service-gmail, background-utils-service-my
- Scripts for service running (PowerShell and Bash)
- Installed dev tooling (pytest, ruff, mypy) and added smoke tests
- Moved Memory Bank to root-level `memory-bank/` and updated rules
- Added psutil, pystray, Pillow, plyer, win10toast dependencies

## Decisions and Considerations

- Typer sub-app per domain; lazy registration to keep startup fast
- Keep CLI thin; move reusable logic into `utils` for services/testing
- Strict typing with mypy; pydantic v2 for validated settings
- Prefer Rich tables/JSON for human/machine-friendly output
- Platform specificity for Wi‑Fi (Windows); add guards/messaging elsewhere
- **CRITICAL TRAY LESSONS LEARNED**:
  - pystray is more reliable than native Win32 Shell_NotifyIcon on Windows 11
  - Menu handlers must run in background threads to avoid blocking pystray event loop
  - Never call `_ensure_manager()` from menu handlers - use existing manager reference
  - Use `icon.run()` in daemon thread rather than `run_detached()` for better callback reliability
  - Explicit visibility toggling on startup helps shell recognition
  - `os._exit(0)` prevents ghost icons under pythonw
- **GMAIL SERVICE LESSONS LEARNED**:
  - Gmail IMAP search `UID X:*` can include boundary UID X in results
  - Must explicitly filter UIDs to prevent duplicate notifications
  - Persistent UID cache essential for service restart continuity
  - Use Gmail App Passwords instead of main password for security

## Next Steps

1) Tests & CI
   - Add Typer CLI invocation tests and output assertions
   - Add service loop tests (short interval) and coverage reporting
   - Create CI workflow (lint, type-check, tests)
2) Documentation
   - Expand README usage for Wi‑Fi, platform/permission requirements
   - Document service manager, tray usage, background start methods (Start-Process, Win+R, pythonw), and log file path
   - Document individual service entry points
3) Utilities Extraction
   - Extract Wi‑Fi logic to `src/background_utils/utils/wifi.py`
   - Add platform detection and graceful handling on non-Windows
4) Feature Roadmap
   - Add more personal automations and production services
   - Develop additional sandbox processes for system monitoring

## Documentation Achievements

- **CLAUDE.md**: Created comprehensive guidance file for future Claude Code instances covering:
  - Development commands (install, lint, test)
  - Architecture overview (CLI + service management systems)
  - Key design patterns for adding services and CLI commands
  - Windows-specific features and integration details

## Important Patterns and Preferences

- Single logging initialization; consistent format
- Environment-based configuration with `.env` template
- Typed functions and testable architecture
- Rich output by default; JSON option where useful
- Combined manager continues remaining services on failure; graceful shutdown with shared stop_event
- **Tray threading model**: pystray in daemon thread, menu handlers spawn background workers, main thread handles KeyboardInterrupt
