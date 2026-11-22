# Ticket Intake

## Purpose

Receive and durably retain domain-agnostic tickets from API clients for later inspection.

## ADDED Requirements

### Requirement: Create a ticket
The API SHALL accept a ticket with a non-empty subject and description, assign an identifier and receipt timestamp, and return the persisted ticket only after the write commits.

#### Scenario: Valid ticket received
- **WHEN** a client submits a valid subject and description
- **THEN** the API returns HTTP 201 with the generated identifier, receipt timestamp, subject, and description
- **AND** the ticket remains available after an API restart

#### Scenario: Invalid ticket
- **WHEN** the subject or description is missing, empty, or whitespace only
- **THEN** the API rejects the request with a validation error and stores no ticket

#### Scenario: Storage unavailable
- **WHEN** persistence fails during creation
- **THEN** the API reports failure and does not report the ticket as created

### Requirement: Retry ticket creation safely
The API SHALL accept an optional client-provided idempotency key, associating it durably with a successful creation and its submitted content.

#### Scenario: Retry with the same key and content
- **WHEN** a client repeats a successful request with the same key and content
- **THEN** the API returns the original ticket without creating another

#### Scenario: Concurrent requests with the same key and content
- **WHEN** clients submit concurrent requests with the same key and content
- **THEN** at most one ticket is created and successful responses refer to that ticket

#### Scenario: Key reused with different content
- **WHEN** a client reuses a key with different subject or description
- **THEN** the API returns HTTP 409 and creates no additional ticket

#### Scenario: No key provided
- **WHEN** a client submits valid requests without a key
- **THEN** each successful request creates a separate ticket

### Requirement: Intake is independent of processing
Ticket creation SHALL NOT depend on a queue, worker, classification, or model provider.

#### Scenario: No processing services configured
- **WHEN** a valid ticket is submitted with only the API and its database available
- **THEN** the API can persist the ticket without creating or claiming a processing result
