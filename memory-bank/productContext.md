# Product Context: background-utils

## Why this project exists
To centralize personal automation and production tools into a single, cohesive Python package. It standardizes how small utilities and background services are built, configured, and executed.

## Problems it solves
- Scattered scripts with duplicated setup and logging
- Inconsistent configuration handling across tools
- No unified CLI for discovery and usage
- Lack of standard service skeleton for background tasks

## How it works
- A single installable package providing:
  - A Typer-based CLI (`background-utils`) with discoverable subcommands
  - A combined service runner (`background-utils-service`) that starts multiple services concurrently and integrates a Windows tray icon (pystray) to Stop/Restart services and View Log
  - Individual service runners for targeted runs (`background-utils-service-example`, `background-utils-service-battery`, `background-utils-service-my`)
  - Shared settings via pydantic-settings with `.env` support
  - Unified logging via Loguru with Rich output and a rotating file sink at `%LOCALAPPDATA%/background-utils/background-utils.log` (Windows)
- Extensible structure to add new CLIs/services with minimal boilerplate

## Current user experience
- `pip install -e .[dev]` gets developers productive fast
- `background-utils --help` lists command groups (e.g., `example`, `wifi`)
- Commands provide styled output with Rich and clear error handling
- Services start cleanly, log consistently, and shut down gracefully
- `.env.example` guides configuration setup

## Roadmap-oriented UX additions
- Detailed README usage snippets for each command
- Platform notes and permission requirements (e.g., `netsh` admin privileges)
- Consistent JSON output options for scripting where applicable