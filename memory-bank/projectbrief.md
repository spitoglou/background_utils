# Project Brief: background-utils

## Purpose
Create a Python 3.12+ project that hosts personal automation and production tools. The project supports:
- Terminal utilities (CLI) using Typer
- Long-running services/daemons
- Shared configuration and logging foundations
- Testable, documented, and extensible structure

## Primary Requirements
- Python 3.12+
- Typer for CLI
- Rich for terminal output
- Pydantic (and pydantic-settings) for configuration
- Loguru for logging
- psutil for system monitoring
- src/ package layout
- Editable install with dev tooling (pytest, pytest-cov, ruff, mypy)
- Example CLI command and example service

## Deliverables
- Working package installable via `pip install -e .[dev]`
- CLI entry point `background-utils`
- Service entry points:
  - Combined manager: `background-utils-service` (with Windows tray icon)
  - Individual services: `background-utils-service-example`, `background-utils-service-battery`, `background-utils-service-my`
- Examples demonstrating CLI, service, and sandbox usage
- Initial tests
- Documentation and helper scripts