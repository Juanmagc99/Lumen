# Spec Delta

## MODIFIED Requirements

### Requirement: Read-only inbox
The SPA SHALL display a list of tickets and let the operator open a detail view and return to the list. The interface SHALL NOT offer ticket creation, editing of ticket subject or description, or deletion; it SHALL allow retrying a failed classification and writing, editing, and approving a response in ticket detail.

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

#### Scenario: Respond to a ticket
- **WHEN** the operator opens ticket detail
- **THEN** the operator can write, save, edit, and approve its response
