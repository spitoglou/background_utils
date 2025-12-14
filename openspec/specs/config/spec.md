# Configuration System Specification

## Purpose

Provide environment-based settings management using Pydantic.

## Requirements

### Requirement: Pydantic Settings

The system SHALL use Pydantic Settings for configuration management.

#### Scenario: Settings Loading
- **WHEN** application starts
- **THEN** load settings from environment variables and .env file

### Requirement: Environment Variable Prefix

The system SHALL use BGU_ prefix for all environment variables.

#### Scenario: Prefixed Variables
- **WHEN** setting BGU_LOG_LEVEL environment variable
- **THEN** configuration system recognizes and uses the value

### Requirement: Default Values

The system SHALL provide sensible default values.

#### Scenario: Default Log Level
- **WHEN** BGU_LOG_LEVEL not set
- **THEN** use INFO as default log level

#### Scenario: Default Service Interval
- **WHEN** BGU_SERVICE_INTERVAL_SECONDS not set
- **THEN** use 5.0 seconds as default interval

### Requirement: Runtime Validation

The system SHALL validate configuration values at runtime.

#### Scenario: Invalid Service Interval
- **WHEN** BGU_SERVICE_INTERVAL_SECONDS set to invalid value
- **THEN** raise validation error

### Requirement: Environment File Support

The system SHALL support .env file for configuration.

#### Scenario: Dotenv Loading
- **WHEN** .env file exists
- **THEN** load configuration from .env file

## Technical Patterns

- Pydantic Settings with environment variable prefix
- Runtime validation of configuration values
- .env file support with example template
- Type-safe configuration access
- Default values with override capability