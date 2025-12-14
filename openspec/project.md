# Project Context

## Purpose

**background-utils** is a personal automation and productivity toolkit for Python 3.12+. The project provides:

- **CLI Tools**: Typer-based command-line utilities for common tasks
- **Background Services**: Long-running services with system tray integration (Windows)
- **Desktop Notifications**: Gmail monitoring and alert system
- **System Utilities**: Wi-Fi management, battery monitoring, and more

**Primary Goals:**
- Automate repetitive personal tasks
- Provide reliable background services with proper Windows integration
- Offer cross-platform CLI tools with rich output
- Maintain clean, testable, and maintainable codebase

## Tech Stack

### Core Technologies
- **Python 3.12+**: Primary language with modern type hints
- **Typer**: CLI framework for building command-line interfaces
- **Rich**: Beautiful console output and formatting
- **Pydantic v2**: Data validation and settings management
- **Pydantic Settings**: Environment variable configuration
- **Loguru**: Flexible and powerful logging

### Service-Specific Dependencies
- **Pystray**: System tray integration for Windows
- **Pillow**: Image handling for tray icons
- **PyWin32**: Windows-specific utilities
- **Plyer**: Cross-platform desktop notifications
- **Win10Toast**: Windows 10+ notification support
- **Psutil**: System monitoring (battery, processes)

### Development & Testing
- **Pytest**: Testing framework with comprehensive coverage
- **Ruff**: Fast Python linter (E, F, I, UP, B rules)
- **Mypy**: Static type checking with strict mode
- **Pytest-cov**: Test coverage reporting
- **Pytest-timeout**: Prevent hanging tests
- **Pytest-mock**: Mocking utilities for test isolation

### Testing Requirements
- **Minimum Coverage**: 85% overall test coverage
- **Core Modules**: 90%+ coverage for config, logging
- **Services**: 85%+ coverage for all services
- **CLI Commands**: 80%+ coverage for CLI functionality
- **CI/CD Integration**: GitHub Actions for automated testing
- **Test Organization**: Mirror structure in tests/ directory

### Build & Packaging
- **Setuptools**: Package building and distribution
- **UV**: Python package management (alternative to pip)

## Project Conventions

### Code Style

**Formatting & Linting:**
- Line length: 100 characters
- Ruff configuration: `select = ["E", "F", "I", "UP", "B"]`
- No ignored lint rules (`ignore = []`)
- Type hints required for all functions

**Naming Conventions:**
- `snake_case` for variables, functions, and modules
- `PascalCase` for classes and type aliases
- `UPPER_CASE` for constants and environment variables
- Prefix private members with underscore `_`

**File Organization:**
- Source code in `src/background_utils/` directory
- Tests in `tests/` directory with mirror structure
- Configuration via `pyproject.toml`

### Architecture Patterns

**Service Architecture:**
- **Cooperative Shutdown**: Services use `threading.Event` for graceful termination
- **Thread-Based**: Each service runs on dedicated thread
- **Shared Stop Event**: Global stop event for coordinated shutdown
- **Timeout-Based**: 10-second timeout for service termination

**CLI Architecture:**
- **Typer App**: Main CLI entry point with subcommands
- **Modular Commands**: Commands organized in `cli/commands/` directory
- **Rich Output**: Colorful, formatted console output
- **JSON Support**: Alternative output format for scripting

**Configuration Pattern:**
- **Pydantic Settings**: Environment-based configuration
- **Prefix-Based**: `BGU_` prefix for all environment variables
- **Validation**: Runtime validation of configuration values
- **Default Values**: Sensible defaults with override capability

**Logging Pattern:**
- **Loguru**: Primary logging framework
- **Dual Sinks**: Console + file logging
- **Windows-Specific**: Logs stored in `%LOCALAPPDATA%\background-utils\`
- **Rotation**: 5MB rotation with 5 file retention

### Testing Strategy

**Test Coverage:**
- Unit tests for core functionality
- Integration tests for CLI commands
- Service tests with cooperative loops
- GUI component mocking for headless testing

**Test Conventions:**
- **Isolation**: Each test runs with clean environment
- **Thread Safety**: Proper cleanup of threads after tests
- **Mocking**: External dependencies mocked for reliability
- **Timeouts**: 30-second timeout to prevent hanging

**Test Fixtures:**
- `cleanup_environment`: Thread cleanup and GUI mocking
- `isolate_logging`: Loguru handler isolation
- `mock_gui_components`: Pystray and GUI component mocking
- `quick_intervals`: Fast service intervals for testing

**Test Execution:**
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term

# Run specific test
uv run pytest tests/test_suite.py::test_cli_root_help
```

### Git Workflow

**Branching Strategy:**
- `main`: Primary development branch
- `mistral`: Current working branch (feature development)
- Feature branches: Short-lived, prefixed with `feat/`, `fix/`, `docs/`, etc.

**Commit Conventions:**
- **Format**: `<type>(scope): description`
- **Types**: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`
- **Scope**: Module or component affected (e.g., `wifi`, `services`, `cli`)
- **Examples**:
  - `feat(wifi): improve error handling for Windows Wi-Fi service issues`
  - `test(core): improve test reliability and cleanup for service components`
  - `docs: add memory bank framework and Gmail setup documentation`

**Merge Strategy:**
- Regular merges from `main` to feature branches
- Pull requests for feature completion
- Squash merges for clean history

## Domain Context

### Background Services

The project focuses on **personal automation services** that run in the background:

- **System Tray Integration**: Windows-specific tray icon for service management
- **Service Lifecycle**: Start, stop, restart capabilities with graceful shutdown
- **User Interaction**: Desktop notifications and tray menu options

### Windows-Specific Considerations

- **Tray Icon**: Reliable Windows 11 tray icon behavior
- **Service Management**: Windows Wireless AutoConfig Service (wlansvc) dependencies
- **File Locations**: `%LOCALAPPDATA%` for logs and configuration
- **Administrator Privileges**: Required for certain Wi-Fi operations

### Gmail Notification Service

- **App Passwords**: Required for secure Gmail access (2FA enabled)
- **IMAP Protocol**: Used for monitoring new emails
- **Desktop Notifications**: Windows 10+ toast notifications
- **State Persistence**: Remembers last processed email across restarts

## Important Constraints

### Technical Constraints

- **Python 3.12+**: Minimum version requirement
- **Windows Focus**: Primary platform for service features
- **Thread Safety**: Services must handle cooperative shutdown
- **Resource Limits**: Services must be lightweight and efficient

### Security Constraints

- **Gmail Access**: Requires App Passwords (never main password)
- **Environment Variables**: Sensitive data in `.env` (never committed)
- **Logging**: No sensitive data in logs
- **Error Handling**: Graceful degradation on permission errors

### Platform Constraints

- **Windows Required**: System tray and Wi-Fi features are Windows-only
- **Administrator Rights**: Some Wi-Fi commands require admin privileges
- **Service Dependencies**: Wireless AutoConfig Service must be running

## External Dependencies

### Key Services

- **Google Gmail IMAP**: Email monitoring and notifications
- **Windows Wireless AutoConfig Service**: Wi-Fi network management
- **Windows Notification System**: Desktop alerts

### Critical APIs

- **IMAP Protocol**: Gmail email access
- **Windows API**: System tray integration via PyWin32
- **Netsh Command**: Wi-Fi profile management

### Build & Development Tools

- **UV**: Python package management
- **GitHub**: Version control and collaboration
- **AI Assistants**: Claude, Kilo Code, Qwen3, Kimi2 for development support
