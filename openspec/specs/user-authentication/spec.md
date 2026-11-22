# user-authentication Specification

## Purpose

Identify individual users and manage access to a shared workspace through revocable sessions.

## Requirements

### Requirement: Authenticate an active account
The system SHALL allow an active user to sign in with an individual username and password and establish a time-limited session.

#### Scenario: Valid credentials
- **WHEN** an active user submits valid credentials
- **THEN** a session is established and the workspace becomes available according to the user's current role

#### Scenario: Invalid or inactive account
- **WHEN** credentials are invalid or the account is inactive
- **THEN** sign-in is denied with a generic failure message and no session is issued

### Requirement: End and expire sessions
The system SHALL allow a user to sign out and SHALL reject expired or revoked sessions.

#### Scenario: Sign out
- **WHEN** a user signs out
- **THEN** the current session is invalidated and cannot be reused

#### Scenario: Session expires
- **WHEN** an expired session requests a protected operation
- **THEN** access is denied and the user can sign in again

### Requirement: Protect credentials and sessions
The system SHALL store passwords using a salted password hash and SHALL protect session credentials from disclosure and cross-site request forgery.

#### Scenario: Stored credentials are inspected
- **WHEN** account or session records are inspected
- **THEN** they do not contain plaintext passwords or reusable session credentials

#### Scenario: Cross-site state-changing request
- **WHEN** a state-changing browser request lacks the required origin or request-forgery protection
- **THEN** the request is rejected without performing the operation

### Requirement: Manage accounts
The system SHALL allow administrators to create accounts, assign roles, reset passwords and activate or deactivate accounts without exposing existing passwords.

#### Scenario: Deactivate an account
- **WHEN** an administrator deactivates an account
- **THEN** its sessions are revoked and it cannot sign in until reactivated

#### Scenario: Reset a password
- **WHEN** an administrator resets a password
- **THEN** previous sessions are revoked and the previous password no longer authenticates

### Requirement: Preserve administrative access
The system SHALL prevent the last active administrator from being deactivated or demoted and SHALL provide a documented local recovery procedure.

#### Scenario: Last administrator removal
- **WHEN** an operation would remove the last active administrator
- **THEN** it is rejected and the account remains unchanged

### Requirement: Bootstrap the first administrator
The system SHALL provide local bootstrap procedures that create the first administrator only when no user accounts exist and do not use committed credentials. The local development launcher SHALL support optional administrator credentials supplied via its environment.

#### Scenario: Bootstrap an existing installation
- **WHEN** bootstrap is attempted after any account exists
- **THEN** no new account is created and existing data is unchanged

#### Scenario: Start with a fresh local database
- **WHEN** the local development launcher applies migrations to a database with no accounts and both administrator environment settings are provided
- **THEN** it creates the first administrator using those settings without displaying or committing the password

### Requirement: Limit sign-in attempts
The system SHALL limit repeated failed sign-in attempts and return a generic failure without revealing whether an account exists.

#### Scenario: Repeated failures
- **WHEN** sign-in attempts exceed the configured limit
- **THEN** further attempts are temporarily refused and no session is issued
