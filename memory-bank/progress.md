# Progress: background-utils

## What works
- Editable install with dependencies and developer tooling
- Typer-based CLI entry `background-utils`
- CLI command groups:
  - `example` with `hello`, `time`
  - `wifi` with `show-passwords` (Windows-only), Rich table or JSON output
- Example long-running service entry `background-utils-service` with graceful shutdown
- Infinite background process entry `background-utils-sandbox` for system monitoring
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
- Foundation complete and operational
- First real-world utility (Wi‑Fi passwords) integrated and accessible
- Sandbox process for system monitoring implemented
- Ready for iterative improvements in tests, CI, and documentation

## Known issues / considerations
- Wi‑Fi command relies on `netsh` and may require admin privileges; permission errors should be handled
- Platform-specific commands need guards or alternative implementations

## Next milestones
1) Add CLI tests and coverage reporting
2) Introduce CI workflow (lint, type-check, tests)
3) Extract Wi‑Fi logic to `utils/` and add platform checks
4) Expand README with detailed command usage and troubleshooting
5) Add more sandbox processes for system monitoring