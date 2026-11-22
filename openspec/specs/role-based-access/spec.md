# role-based-access Specification

## Purpose

Restrict shared workspace operations to authenticated users according to their current role.

## Requirements

### Requirement: Enforce access on the server
The system SHALL require authentication and authorize every application API operation on the server, except sign-in and process health. Missing or invalid sessions SHALL receive 401 and insufficient permissions SHALL receive 403.

#### Scenario: Direct anonymous request
- **WHEN** an unauthenticated client calls a protected endpoint directly
- **THEN** the server denies access without exposing protected data or performing the operation

#### Scenario: Restricted operation
- **WHEN** an authenticated operator calls an administrator-only endpoint
- **THEN** the server denies the operation without changing data

#### Scenario: Public health
- **WHEN** an anonymous client requests process health
- **THEN** process availability remains accessible independently of authentication and storage

### Requirement: Assign shared workspace permissions
The system SHALL support administrator and operator roles. Both roles SHALL access shared tickets, responses, generation, and knowledge management. Only administrators SHALL manage accounts and classification options; both roles SHALL read options needed for ticket work.

#### Scenario: Operator reviews a ticket
- **WHEN** an operator creates or classifies a ticket, manages knowledge, drafts or approves a response, or requests a generation
- **THEN** the operation is permitted within existing workflow constraints

#### Scenario: Operator changes options
- **WHEN** an operator attempts to create or modify a classification option
- **THEN** the operation is denied

#### Scenario: Administrator manages users
- **WHEN** an administrator manages another account or classification options
- **THEN** the operation is permitted subject to account safety rules

### Requirement: Apply current account status and role
The system SHALL enforce the current stored account status and role on protected requests, including for existing sessions.

#### Scenario: Role changes during a session
- **WHEN** a user's role changes while a session exists
- **THEN** subsequent requests use the updated permissions

### Requirement: Present authorized actions
The workspace SHALL show the signed-in identity and role, provide sign-out, and expose only actions allowed for that role. It SHALL communicate authentication expiry and authorization failures without silently losing unsaved response text.

#### Scenario: Session expires during editing
- **WHEN** a protected save fails because the session has expired
- **THEN** the user is prompted to sign in again and unsaved response text remains recoverable

### Requirement: Preserve existing shared data
The system SHALL retain existing tickets, responses, documents, options, and provenance when authentication is introduced, and authorized users SHALL continue to access them as shared data.

#### Scenario: Upgrade an existing installation
- **WHEN** an administrator bootstraps an installation with existing workspace data
- **THEN** authorized users can access the existing data without assigning ownership or migrating it to separate groups
