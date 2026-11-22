## MODIFIED Requirements

### Requirement: Read-only inbox
The SPA SHALL display a list of tickets and let the operator open a detail view and return to the list. The interface SHALL NOT offer ticket creation, editing, or deletion; it SHALL allow retrying a failed classification.

#### Scenario: Browse and inspect
- **WHEN** the operator opens a ticket from the inbox
- **THEN** the detail shows its subject, description, identifier, and receipt timestamp
- **AND** the operator can return to the inbox

#### Scenario: Ticket content contains markup
- **WHEN** a ticket includes markup or script-like text
- **THEN** the SPA displays it as text without executing it

#### Scenario: Retry failed classification
- **WHEN** a classification has failed after automatic retries
- **THEN** the ticket detail offers an action to request another attempt
- **AND** reports whether the request succeeded or failed

## ADDED Requirements

### Requirement: Display classification progress
The API and SPA SHALL expose classification status for each ticket and the detail SHALL expose its available result and whether it is simulated.

#### Scenario: Ticket is pending or processing
- **WHEN** classification is pending or processing
- **THEN** its status is visible in the list and detail without presenting a completed result

#### Scenario: Classification is complete
- **WHEN** classification completes
- **THEN** the list and detail show completed status
- **AND** the detail shows the result labelled as simulated

#### Scenario: Classification fails
- **WHEN** automatic attempts are exhausted
- **THEN** the list and detail show failed status and the detail explains that retry is available
