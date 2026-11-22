# Local Development Environment

## Purpose

Provide a consistent way to prepare and operate Lumen's local development services.

## ADDED Requirements

### Requirement: Discover development commands
The project SHALL provide a root-level command interface that lists its available development commands and prerequisites.

#### Scenario: Discover available commands
- **WHEN** a developer requests help
- **THEN** the interface describes setup, start, stop, restart, status, and log commands

### Requirement: Prepare development dependencies
The interface SHALL provide a setup command that installs the project's locked API and web dependencies and reports failures.

#### Scenario: Dependency installation fails
- **WHEN** a required dependency cannot be installed
- **THEN** setup reports the failure and exits unsuccessfully

### Requirement: Start the development environment
The start command SHALL start the local database, apply pending migrations, and start the API and web server in the background in dependency order.

#### Scenario: Successful start
- **WHEN** prerequisites and configuration are available and startup succeeds
- **THEN** the command reports the running services and their local addresses

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

### Requirement: Stop and restart managed services
The interface SHALL provide stop and restart commands that operate only on the intended local development services and retain persisted database data.

#### Scenario: Database shared across checkouts
- **WHEN** developers use the tooling from different checkouts with the same Compose project
- **THEN** those checkouts use the same database and persisted volume
- **AND** stopping that database affects all checkouts using it

#### Scenario: Stop the environment
- **WHEN** a developer requests stop
- **THEN** managed application processes and the project's database service are stopped
- **AND** the database volume is retained

#### Scenario: Stop after a process has exited
- **WHEN** a recorded process has exited or its identifier has been reused
- **THEN** stop does not terminate an unrelated process and reports any state it cannot safely resolve

#### Scenario: Restart the environment
- **WHEN** a developer requests restart
- **THEN** the environment is stopped and started again using the same data
- **AND** startup does not proceed if safe stopping fails

### Requirement: Inspect development services
The interface SHALL provide status and log commands for the database, API, and web server, including actionable information when a service is unavailable.

#### Scenario: Inspect a stopped service
- **WHEN** a developer requests status or logs for a service that is not running
- **THEN** the interface identifies its state or explains that logs are unavailable

### Requirement: Handle local configuration safely
The tooling SHALL use locally supplied database credentials without committing them or printing them in command output or logs.

#### Scenario: Local configuration file
- **WHEN** a developer provides configuration in the root `.env` file
- **THEN** development commands load its supported settings without executing the file
- **AND** the repository ignores `.env` and provides a credential-free `.example.env` template

#### Scenario: Credentials are missing
- **WHEN** startup requires credentials that are not configured
- **THEN** it explains how to supply them and exits without starting dependent services
