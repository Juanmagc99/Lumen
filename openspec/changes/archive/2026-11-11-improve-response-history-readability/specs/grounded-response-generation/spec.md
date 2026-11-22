# Spec Delta

## ADDED Requirements

### Requirement: Present a readable generation history
The system SHALL present each generation as a visually distinct, independently expandable history entry identified by status and creation time. The newest entry SHALL initially be expanded and older entries collapsed. Expanding an entry SHALL make its available original text, warnings, actions, sources, and audit details accessible.

#### Scenario: Review multiple generations
- **WHEN** a ticket has multiple generation records
- **THEN** the operator can distinguish and expand each record without losing access to any original suggestion or its review information
- **AND** the newest record is initially expanded

#### Scenario: Review a long suggestion
- **WHEN** an operator opens a generation containing long or multiline text
- **THEN** the text is readable, preserves its line breaks, and remains accessible on narrow screens

#### Scenario: Generation status refreshes
- **WHEN** generation status refreshes while the operator is inspecting the history
- **THEN** the operator's expanded or collapsed choices for existing entries remain intact
