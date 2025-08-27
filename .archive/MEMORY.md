# Project Memory Bank

## Recent Additions

### Gmail Notification Service (2025-08-14)
**Added**: Comprehensive Gmail notification service with the following features:

**Implementation**:
- `src/background_utils/services/gmail_notifier.py`: Main service implementation
- IMAP over SSL connection to Gmail (`imap.gmail.com:993`)
- UID-based email tracking to prevent duplicate notifications
- Cross-platform notifications using `plyer` with `win10toast` Windows fallback
- Persistent UID cache in `%LOCALAPPDATA%\background-utils\gmail_last_uid.txt`
- 60-second check interval with cooperative threading

**Configuration**:
- Added `gmail_email` and `gmail_password` fields to `config.py`
- Environment variables: `BGU_GMAIL_EMAIL`, `BGU_GMAIL_PASSWORD` 
- Placeholders added to `.env` and `.env.example`

**Service Registration**:
- Added to `_collect_default_services()` in `manager.py`
- Entry point `background-utils-service-gmail` in `pyproject.toml`
- Runs automatically with combined service manager

**Dependencies Added**:
- `plyer>=2.1` for cross-platform notifications
- `win10toast>=0.9` for Windows-specific notifications

**Key Features**:
- Only monitors INBOX folder
- Shows desktop notifications with sender and subject
- Handles multiple new emails in single check
- Proper error handling and automatic reconnection
- Debug logging for troubleshooting
- Security-focused (recommends App Passwords)

**Documentation Updated**:
- `CLAUDE.md`: Added Gmail service to commands and detailed service documentation
- `README.md`: Added Gmail service to individual service entry points
- `.env.example`: Added Gmail credential placeholders

**Troubleshooting Notes**:
- Gmail IMAP search behavior: `UID X:*` can include boundary UID X in results
- Fixed with explicit UID filtering to prevent duplicate notifications
- UID cache survives service restarts to maintain state consistency