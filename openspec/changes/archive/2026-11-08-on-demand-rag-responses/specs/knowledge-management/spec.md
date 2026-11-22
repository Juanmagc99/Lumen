# Spec Delta

## Purpose

Let operators maintain versioned knowledge for grounded ticket response generation.

## ADDED Requirements

### Requirement: Manage knowledge bases
The system SHALL allow operators to create, list, and select knowledge bases and inspect their documents and processing status.

#### Scenario: Select a knowledge base
- **WHEN** an operator opens the knowledge workspace
- **THEN** available knowledge bases and their documents are visible for selection

### Requirement: Add documents and text
The system SHALL accept uploaded UTF-8 plain text and Markdown documents and directly entered nonblank text into a selected knowledge base. It SHALL clearly communicate supported formats and configured size limits.

#### Scenario: Add knowledge
- **WHEN** an operator submits supported nonempty content within the configured limit
- **THEN** the system persists a version and exposes its processing status

#### Scenario: Reject unsupported content
- **WHEN** content is empty, exceeds the limit, cannot be decoded, or has an unsupported format
- **THEN** the system reports the reason and does not claim it is available for retrieval

### Requirement: Version knowledge
The system SHALL preserve immutable content versions and allow an operator to update or deactivate a document without invalidating references to previous versions.

#### Scenario: Update a document
- **WHEN** an operator replaces document content
- **THEN** a new version is processed and earlier citations remain inspectable

#### Scenario: Deactivate a document
- **WHEN** an operator deactivates a document
- **THEN** it is excluded from new retrievals while historical citations remain inspectable

### Requirement: Expose ingestion state
The system SHALL make pending, processing, ready, and failed processing states visible and allow retry of failed processing.

#### Scenario: Processing fails
- **WHEN** a document cannot be processed
- **THEN** it is not presented as searchable and the operator can see the failure and request a retry
