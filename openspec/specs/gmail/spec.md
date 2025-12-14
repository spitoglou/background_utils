# Gmail Notification Service Specification

## Purpose

Monitor Gmail inbox and display desktop notifications for new emails.

## Requirements

### Requirement: IMAP Connection

The system SHALL connect to Gmail IMAP server using SSL on port 993.

#### Scenario: Successful Connection
- **WHEN** valid Gmail credentials provided
- **THEN** establish IMAP connection to imap.gmail.com:993

#### Scenario: Connection Error Handling
- **WHEN** connection fails
- **THEN** log error and attempt automatic reconnection

### Requirement: UID-Based Email Tracking

The system SHALL use UID-based tracking to identify new emails.

#### Scenario: Track New Emails
- **WHEN** new email arrives with higher UID than last processed
- **THEN** display desktop notification

#### Scenario: Persistent UID Cache
- **WHEN** service restarts
- **THEN** load last processed UID from cache file

### Requirement: Desktop Notifications

The system SHALL display cross-platform desktop notifications for new emails.

#### Scenario: Windows Notification
- **WHEN** new email arrives on Windows
- **THEN** display Windows 10+ toast notification

#### Scenario: Cross-Platform Notification
- **WHEN** new email arrives on other platforms
- **THEN** use plyer for cross-platform notification

### Requirement: Configuration

The system SHALL support configuration via environment variables.

#### Scenario: Email Configuration
- **WHEN** BGU_GMAIL_EMAIL and BGU_GMAIL_PASSWORD set
- **THEN** use credentials for Gmail connection

#### Scenario: Check Interval
- **WHEN** BGU_SERVICE_INTERVAL_SECONDS configured
- **THEN** use specified interval for email checks

### Requirement: Security

The system SHALL require Gmail App Passwords for authentication.

#### Scenario: App Password Requirement
- **WHEN** user configures Gmail service
- **THEN** documentation requires App Password instead of main password

#### Scenario: Environment Variable Security
- **WHEN** storing credentials
- **THEN** use .env file (never commit to version control)

## Technical Patterns

- IMAP over SSL connection to Gmail
- UID-based email tracking with persistent cache
- Cross-platform notification fallback (plyer + win10toast)
- Cooperative threading with 60-second check interval
- Automatic reconnection on connection errors
- UID filtering to prevent duplicate notifications

## Additional Context

**Implementation Details:**
- See [Active Context - Gmail Service](memory-bank/activeContext.md#gmail-service)
- Gmail IMAP UID boundary issue resolved
- Persistent UID cache for service restart continuity

**Security Requirements:**
- Requires Gmail App Passwords (never main password)
- Configuration via environment variables only
- See [Tech Context - Security](memory-bank/techContext.md#security-constraints)