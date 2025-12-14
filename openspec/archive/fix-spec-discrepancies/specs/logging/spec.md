## MODIFIED Requirements

### Requirement: Logging Levels

The system SHALL support configurable logging levels via the `BGU_LOG_LEVEL` environment variable.

#### Scenario: Debug Level
- **WHEN** BGU_LOG_LEVEL set to DEBUG
- **THEN** display debug-level messages

#### Scenario: Info Level
- **WHEN** BGU_LOG_LEVEL set to INFO (default)
- **THEN** display info-level and higher messages

#### Scenario: Environment Variable Prefix Consistency
- **WHEN** configuring logging via environment variables
- **THEN** use BGU_LOG_LEVEL (consistent with project BGU_ prefix convention)
- **AND** LOG_LEVEL without prefix is not recognized
