# background-utils

Personal automation and production tools for Python 3.12+. Includes Typer-based CLIs and long-running services with Pydantic config, Loguru logging, and Rich output.

## Quick start

1) Install (with UV):
    uv sync --extra dev

2) Run CLI:
    background-utils --help

3) Run services with system tray (Windows):
    background-utils-service

## Project structure

- src/background_utils: package code
  - cli: Typer app and commands
  - services: long-running workers/daemons
  - utils: shared helpers
  - config.py: settings via pydantic-settings
  - logging.py: loguru configuration
- scripts: helpers for service process management
- tests: pytest tests

## Services and System Tray (Windows)

The main service entry point `background-utils-service` launches a system tray icon that manages long-running services:

- **Tray Menu Options:**
  - **View Log**: Opens the log file in Notepad (%LOCALAPPDATA%\background-utils\background-utils.log)
  - **Stop Services**: Gracefully stops all running services
  - **Restart Services**: Stops current services and starts fresh instances
  - **Exit**: Stops services and exits the application

- **Service Management:**
  - Services run on dedicated threads with cooperative shutdown via shared stop_event
  - Graceful shutdown with 10-second timeout for each service
  - Individual service entry points available for testing:
    - background-utils-service-example
    - background-utils-service-battery
    - background-utils-service-gmail
    - background-utils-service-my

- **Windows Compatibility:**
  - Fully functional on Windows 11 with reliable tray icon behavior
  - No ghost icons - proper cleanup on exit
  - Responsive tray menu with non-blocking operations
  - Ctrl+C support for console-based shutdown

## Gmail Notification Setup

The Gmail notification service monitors your Gmail inbox and shows desktop notifications for new emails. To configure it securely:

### Step 1: Enable 2-Factor Authentication

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification if not already enabled
3. This is required for App Passwords

### Step 2: Generate an App Password

1. In Google Account Security, go to **App passwords**
2. Select **Mail** as the app and **Windows Computer** as the device
3. Click **Generate** to create a 16-character app password
4. Copy this password (you won't be able to see it again)

### Step 3: Configure Environment Variables

Add your Gmail credentials to the `.env` file:

```bash
# Gmail notification settings
BGU_GMAIL_EMAIL=your-email@gmail.com
BGU_GMAIL_PASSWORD=your-16-char-app-password
```

**Security Notes:**

- Never use your main Gmail password - always use App Passwords
- Never commit the `.env` file to version control (it's already in .gitignore)
- The app password only works for this specific application

### Step 4: Test the Service

```bash
# Test individual Gmail service
background-utils-service-gmail

# Or run with all services
background-utils-service
```

The service will:

- Check for new emails every 60 seconds
- Show desktop notifications with sender and subject
- Remember the last email processed (survives restarts)
- Automatically reconnect on connection errors

**Troubleshooting:**

- If you get authentication errors, verify the App Password is correct
- If notifications don't appear, check that `plyer` and `win10toast` are installed
- Check logs at `%LOCALAPPDATA%\background-utils\background-utils.log`

## Wi-Fi Command Troubleshooting

The Wi-Fi commands (`wifi show-passwords` and `wifi list-networks`) require the Windows Wireless AutoConfig Service to be running.

**Common Error:**

``` bash
❌ Wi-Fi Service Issue
The Wireless AutoConfig Service (wlansvc) is not running.
```

**Solution:**

1. **Quick Fix (temporary):** Run as Administrator:

   ```cmd
   net start wlansvc
   ```

2. **Permanent Fix:** Enable the service to start automatically:

   ```cmd
   sc config wlansvc start= auto
   net start wlansvc
   ```

**Additional Notes:**

- The commands only work on Windows systems with Wi-Fi capability
- `show-passwords` requires Administrator privileges to reveal passwords
- On virtual machines or systems without Wi-Fi, these commands will show appropriate error messages

## Development

- Python 3.12+
- Tooling: ruff, mypy, pytest, pytest-cov

Common commands:

- Lint:
    uv run ruff check .
- Type-check:
    uv run mypy .
- Tests:
    uv run pytest
- Tests with coverage:
    uv run pytest --cov=src/background_utils --cov-report=term
- Run specific test:
    uv run pytest tests/services/test_gmail.py -v
- Run Gmail service tests:
    uv run pytest tests/services/test_gmail.py::TestGmailUtilities -v
- Run tray controller tests:
    uv run pytest tests/services/test_tray_simple.py -v

## Testing Infrastructure

The project includes comprehensive testing with:

- **Test Coverage**: 25%+ and growing (target: 85%+)
- **Gmail Service Tests**: 20+ tests covering core functionality
- **Tray Controller Tests**: 10+ tests for menu actions and lifecycle
- **Service Manager Tests**: Integration tests for multi-service scenarios
- **CI/CD Pipeline**: GitHub Actions workflow with test matrix

### Test Organization

```
tests/
├── services/             # Service tests
│   ├── test_gmail.py      # Gmail notification service tests
│   ├── test_tray.py       # Tray controller tests (comprehensive)
│   └── test_tray_simple.py # Tray controller tests (simplified)
├── conftest.py           # Shared fixtures and utilities
└── test_suite.py         # Existing test suite
```

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v --tb=short

# Run tests with coverage
uv run pytest tests/ --cov=src/background_utils --cov-report=term

# Run specific test module
uv run pytest tests/services/test_gmail.py -v

# Run specific test class
uv run pytest tests/services/test_gmail.py::TestGmailUtilities -v

# Run specific test method
uv run pytest tests/services/test_gmail.py::TestGmailUtilities::test_decode_email_header_simple -v
```

### Test Fixtures

The test suite includes powerful fixtures:

- **mock_imap_connection**: Mock IMAP4_SSL for Gmail testing
- **mock_notifications**: Mock notification system with tracking
- **mock_file_system**: Temporary file system for cache testing
- **mock_gui_components**: Mock GUI components to prevent hanging
- **quick_intervals**: Fast service intervals for testing

### CI/CD Pipeline

The project uses GitHub Actions for continuous integration:

- **Test Matrix**: Python 3.12, 3.13 on Ubuntu and Windows
- **Quality Gates**: Linting, type checking, test coverage
- **Coverage Reporting**: Codecov integration
- **Automated Testing**: Runs on push and pull requests

See `.github/workflows/test_and_ci.yml` for details.

## Test Coverage Goals

- **Core Modules** (config, logging): 90%+
- **Services**: 85%+
- **CLI Commands**: 80%+
- **Overall Project**: 85%+

Current coverage can be checked with:
```bash
uv run pytest tests/ --cov=src/background_utils --cov-report=term
```

## Packaging

- pyproject.toml uses setuptools with package discovery under src/.
- Entry points:
  - background-utils: CLI
  - background-utils-service: combined service manager with system tray

## Development Tools

This project's development was facilitated by AI code assisting tools including:

- **Claude Code**: Interactive CLI development environment
- **Claude Sonnet Models**: Code generation and architectural guidance
- **Kilo Code**: Development assistance and code optimization
- **Qwen3 Code Models**: Code analysis and improvement suggestions
- **Kimi2 Models**: Development workflow automation

These AI tools helped accelerate development, improve code quality, and provide architectural insights throughout the project lifecycle.
