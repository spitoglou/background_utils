# Logging System Specification

## Purpose

Provide unified logging with Rich console output and file-based logging.

## Requirements

### Requirement: Loguru Integration

The system SHALL use Loguru as the primary logging framework.

#### Scenario: Logger Initialization
- **WHEN** application starts
- **THEN** Loguru logger is configured with appropriate sinks

### Requirement: Rich Console Output

The system SHALL provide colorful console output using Rich.

#### Scenario: Console Logging
- **WHEN** log message is generated
- **THEN** display formatted message with Rich styling

### Requirement: File Logging

The system SHALL write logs to file on Windows platforms.

#### Scenario: Windows File Logging
- **WHEN** running on Windows
- **THEN** write logs to %LOCALAPPDATA%\background-utils\background-utils.log

#### Scenario: Log Rotation
- **WHEN** log file reaches 5MB
- **THEN** rotate logs and keep 5 previous files

### Requirement: Logging Levels

The system SHALL support configurable logging levels.

#### Scenario: Debug Level
- **WHEN** BGU_LOG_LEVEL set to DEBUG
- **THEN** display debug-level messages

#### Scenario: Info Level
- **WHEN** BGU_LOG_LEVEL set to INFO (default)
- **THEN** display info-level and higher messages

### Requirement: Idempotent Setup

The system SHALL ensure logging setup is idempotent.

#### Scenario: Multiple Setup Calls
- **WHEN** setup_logging called multiple times
- **THEN** only configure logger on first call

## Technical Patterns

- Loguru with Rich console sink
- Windows-specific file logging with rotation
- Environment-based level configuration
- Idempotent setup with global state tracking