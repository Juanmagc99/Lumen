## MODIFIED Requirements

### Requirement: Start the development environment
The start command SHALL start the local database, apply pending migrations, and start the API, worker, and web server in the background in dependency order.

#### Scenario: Successful start
- **WHEN** prerequisites and configuration are available and startup succeeds
- **THEN** the command reports the running services and their local addresses where applicable

#### Scenario: Required step fails
- **WHEN** a prerequisite, database startup, migration, or application startup fails
- **THEN** the command reports the failure without claiming the environment is fully running
- **AND** it describes or cleans up services started by the failed invocation

#### Scenario: Start is repeated
- **WHEN** the environment is already running and start is requested again
- **THEN** the command avoids launching duplicate managed services and reports their state

#### Scenario: Port is occupied by an unrelated process
- **WHEN** a required port is occupied by an unrelated process
- **THEN** startup reports the conflict without terminating or adopting that process

### Requirement: Inspect development services
The interface SHALL provide status and log commands for the database, API, worker, and web server, including actionable information when a service is unavailable.

#### Scenario: Inspect a stopped service
- **WHEN** a developer requests status or logs for a service that is not running
- **THEN** the interface identifies its state or explains that logs are unavailable

### Requirement: Handle local configuration safely
The tooling SHALL use locally supplied database user, password, and database name consistently for the database, API, worker, and migrations without committing credentials or printing them in command output or logs.

#### Scenario: Local configuration file
- **WHEN** a developer provides configuration in the root `.env` file
- **THEN** development commands load its supported settings without executing the file
- **AND** the repository ignores `.env` and provides a credential-free `.example.env` template

#### Scenario: Credentials are missing
- **WHEN** startup requires credentials that are not configured
- **THEN** it explains how to supply them and exits without starting dependent services
