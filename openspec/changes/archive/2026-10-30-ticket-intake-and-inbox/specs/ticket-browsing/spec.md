# Ticket Browsing

## Purpose

Let operators inspect received tickets through a read-only API and web inbox.

## ADDED Requirements

### Requirement: List tickets
The API SHALL return all persisted tickets ordered by receipt timestamp descending, with a deterministic order for ties. Each entry SHALL include its identifier, subject, and receipt timestamp.

#### Scenario: Tickets exist
- **WHEN** a client requests the ticket list
- **THEN** the response contains the persisted tickets with the most recently received first

#### Scenario: No tickets exist
- **WHEN** a client requests the ticket list and no tickets exist
- **THEN** the API returns an empty collection

### Requirement: Retrieve a ticket
The API SHALL return a ticket's identifier, subject, description, and receipt timestamp when requested by its identifier.

#### Scenario: Existing ticket
- **WHEN** a client requests an existing ticket
- **THEN** the API returns the stored ticket data

#### Scenario: Unknown ticket
- **WHEN** a client requests a well-formed identifier that does not match a ticket
- **THEN** the API returns HTTP 404

### Requirement: Read-only inbox
The SPA SHALL display a list of tickets and let the operator open a detail view and return to the list. The interface SHALL NOT offer ticket creation, editing, or deletion.

#### Scenario: Browse and inspect
- **WHEN** the operator opens a ticket from the inbox
- **THEN** the detail shows its subject, description, identifier, and receipt timestamp
- **AND** the operator can return to the inbox

#### Scenario: Ticket content contains markup
- **WHEN** a ticket includes markup or script-like text
- **THEN** the SPA displays it as text without executing it

### Requirement: Communicate loading and failure states
The SPA SHALL make loading, empty, unavailable, and missing-ticket states understandable and offer a way to retry or return where appropriate.

#### Scenario: Empty inbox
- **WHEN** the ticket list is successfully loaded and contains no tickets
- **THEN** the SPA shows an empty state

#### Scenario: Request fails
- **WHEN** a list or detail request fails
- **THEN** the SPA shows an error and offers a retry or a return to the inbox

#### Scenario: Ticket does not exist
- **WHEN** the requested ticket is not found
- **THEN** the SPA explains that it is unavailable and offers a return to the inbox
