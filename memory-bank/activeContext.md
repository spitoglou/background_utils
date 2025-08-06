# Active Context: background-utils

## Current Focus
- Foundation scaffold for CLIs, services, and sandbox processes is in place
- Integrated first real utility: Wi‑Fi password viewer (Windows)
- Next: expand tests/CI and documentation

## Recent Changes
- Established src-layout Python 3.12+ package with Typer CLI and example service
- Implemented shared logging (Loguru + Rich) and configuration (pydantic-settings)
- Added CLI command groups:
  - example (hello, time)
  - wifi (show-passwords) — Windows-only via `netsh`, table/JSON output
- Registered CLI, service, and sandbox entry points via pyproject
- Added scripts for service running (PowerShell and Bash)
- Installed dev tooling (pytest, ruff, mypy) and added smoke tests
- Moved Memory Bank to root-level `memory-bank/` and updated rules
- Added psutil dependency for system monitoring capabilities

## Decisions and Considerations
- Typer sub-app per domain; lazy registration to keep startup fast
- Keep CLI thin; move reusable logic into `utils` for services/testing
- Strict typing with mypy; pydantic v2 for validated settings
- Prefer Rich tables/JSON for human/machine-friendly output
- Platform specificity for Wi‑Fi (Windows); add guards/messaging elsewhere

## Next Steps
1) Tests & CI
   - Add Typer CLI invocation tests and output assertions
   - Add service loop tests (short interval) and coverage reporting
   - Create CI workflow (lint, type-check, tests)
2) Documentation
   - Expand README usage for Wi‑Fi, platform/permission requirements
   - Document adding new CLI groups/services and utils layout
3) Utilities Extraction
   - Extract Wi‑Fi logic to `src/background_utils/utils/wifi.py`
   - Add platform detection and graceful handling on non-Windows
4) Feature Roadmap
   - Add more personal automations and production services
   - Develop additional sandbox processes for system monitoring

## Important Patterns and Preferences
- Single logging initialization; consistent format
- Environment-based configuration with `.env` template
- Typed functions and testable architecture
- Rich output by default; JSON option where useful