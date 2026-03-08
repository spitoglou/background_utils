# background-utils

Personal automation and production tools for Python 3.12+. Includes Typer-based CLIs and long-running services with Pydantic config, Loguru logging, and Rich output.

## Quick Start

```bash
# 1. Install (with UV)
uv sync --extra dev

# 2. Run CLI
background-utils --help

# 3. Run services with system tray (Windows)
background-utils-service
```

## Project Structure

```
src/background_utils/
  cli/              # Typer app and commands
  services/         # Long-running workers/daemons
  utils.py          # Shared helpers (interruptible_sleep, etc.)
  config.py         # Settings via pydantic-settings (BGU_ prefix)
  logging.py        # Loguru + Rich configuration
scripts/            # Dev/process helpers
tests/              # pytest suite
```

## Services and System Tray (Windows)

The main entry point `background-utils-service` launches a system tray icon that manages long-running services:

**Tray Menu:**
- **View Log** -- opens `%LOCALAPPDATA%\background-utils\background-utils.log` in Notepad
- **Stop Services** -- gracefully stops all running services
- **Restart Services** -- stops and re-launches services
- **Exit** -- stops services and exits

**Individual service entry points** (for testing):

```bash
background-utils-service-example
background-utils-service-battery
background-utils-service-gmail
background-utils-service-my
```

Services run on dedicated threads with cooperative shutdown via `stop_event` (10-second timeout per service).

## Gmail Notification Setup

The Gmail service monitors your inbox and shows desktop notifications for new emails.

### 1. Enable 2-Factor Authentication

Go to [Google Account Security](https://myaccount.google.com/security) and enable 2-Step Verification.

### 2. Generate an App Password

In Google Account Security > **App passwords**, create a password for Mail on Windows Computer. Copy the 16-character password.

### 3. Configure Environment

Add credentials to `.env`:

```bash
BGU_GMAIL_EMAIL=your-email@gmail.com
BGU_GMAIL_PASSWORD=your-16-char-app-password
```

**Security:** Never use your main Gmail password. Never commit `.env` (it's in `.gitignore`). The `gmail_password` field uses Pydantic `SecretStr` internally.

### 4. Test

```bash
background-utils-service-gmail   # Individual
background-utils-service         # All services
```

The service checks every 60 seconds, shows desktop notifications, persists UID state across restarts, and auto-reconnects on errors.

**Troubleshooting:**
- Authentication errors: verify the App Password
- Missing notifications: check that `plyer` / `win10toast` are installed
- Logs: `%LOCALAPPDATA%\background-utils\background-utils.log`

## Wi-Fi Commands

`wifi show-passwords` and `wifi list-networks` require Windows Wireless AutoConfig Service.

If the service is not running:

```cmd
:: Quick fix (temporary, run as Admin)
net start wlansvc

:: Permanent fix
sc config wlansvc start= auto
net start wlansvc
```

`show-passwords` requires Administrator privileges. On VMs or systems without Wi-Fi, commands show appropriate errors.

## Development

**Requirements:** Python 3.12+, UV

```bash
# Install dev dependencies
uv sync --extra dev

# Lint
uv run ruff check .

# Type-check
uv run mypy .

# Tests
uv run pytest

# Tests with coverage
uv run pytest --cov=src/background_utils --cov-report=term-missing

# Specific tests
uv run pytest tests/services/test_gmail.py -v
uv run pytest tests/services/test_gmail.py::TestGmailUtilities -v
```

### Test Organization

```
tests/
  conftest.py             # Shared fixtures (mock IMAP, notifications, file system, GUI)
  test_suite.py           # CLI, config, battery, example, my_service, manager, tray tests
  services/
    test_gmail.py         # Gmail notification service (55+ tests)
    test_tray.py          # Tray controller + service manager (40+ tests)
```

### CI/CD

GitHub Actions runs on push/PR to `main` and `mistral`:
- **Matrix:** Python 3.12, 3.13 on Ubuntu and Windows
- **Quality gates:** Ruff lint, Mypy type-check (source only), pytest with coverage
- **Coverage:** Uploaded to Codecov from the 3.12/ubuntu cell

See `.github/workflows/test_and_ci.yml`.

### Coverage Targets

| Scope | Target |
|-------|--------|
| Core modules (config, logging) | 90%+ |
| Services | 85%+ |
| CLI commands | 80%+ |
| Overall | 85%+ |

Current overall coverage: ~93% (145 tests passing).

## Packaging

`pyproject.toml` uses setuptools with `src/` layout. Entry points:

- `background-utils` -- CLI
- `background-utils-service` -- combined service manager with system tray
