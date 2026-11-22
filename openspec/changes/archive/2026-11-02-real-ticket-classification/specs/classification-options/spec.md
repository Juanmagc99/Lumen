# Spec Delta

## Purpose

Allow operators to maintain global category and priority options for ticket classification and browsing.

## ADDED Requirements

### Requirement: Manage classification options
The application SHALL let operators list, create, rename, activate, and deactivate global category and priority options. Names SHALL be nonblank and unique within each option type, ignoring case and surrounding whitespace.

#### Scenario: Add an option
- **WHEN** an operator adds a valid category or priority
- **THEN** it is available for subsequent classification

#### Scenario: Duplicate or blank name
- **WHEN** an operator submits a blank or duplicate name in the same option type
- **THEN** the application rejects the change and explains why

#### Scenario: Deactivate an option
- **WHEN** an operator deactivates an option
- **THEN** it is excluded from new model decisions while existing ticket associations remain visible and filterable

#### Scenario: Rename an option
- **WHEN** an option is renamed
- **THEN** existing ticket associations retain their identity and show the current name

### Requirement: Seed initial options
The system SHALL initialize generic editable options once without replacing later operator changes.

#### Scenario: Initial setup
- **WHEN** the options are initialized for the first time
- **THEN** categories include Inquiry, Incident, Request, and Other and priorities include Low, Normal, High, and Urgent

#### Scenario: Repeated startup
- **WHEN** the system starts again after options were edited or deactivated
- **THEN** the operator's changes are preserved
