# Spec Delta

## MODIFIED Requirements

### Requirement: Read-only inbox
The SPA SHALL display a list of tickets and let the operator open a detail view and return to the list. The interface SHALL NOT offer ticket creation, editing of ticket subject or description, or deletion; it SHALL allow editing the ticket's category and priority, retrying a failed classification, and writing, editing, and approving a response in ticket detail.

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

## ADDED Requirements

### Requirement: Present ticket tags
The inbox and detail SHALL present the current category and priority as named colored tags. The detail SHALL place them near the top in separate category and priority rows, with category space able to accommodate multiple tags in a future change. The current assignment remains at most one category and one priority.

#### Scenario: Classified ticket
- **WHEN** a ticket has category and priority values
- **THEN** both names and their configured colors are visible in the list and detail

#### Scenario: Missing or inactive value
- **WHEN** a value is undetermined or its option has been deactivated
- **THEN** the detail identifies that state without inventing a value and existing inactive associations remain visible

### Requirement: Edit ticket tags
The detail SHALL allow an operator to select an active category and priority independently, save changes, and see their current values in the list and detail. It SHALL report errors and reject stale writes without silently replacing newer choices.

#### Scenario: Change a tag
- **WHEN** an operator selects and saves an active option of the correct type
- **THEN** the selection persists and filters use the current assignment

#### Scenario: Invalid or stale selection
- **WHEN** a selected option is inactive, has the wrong type, or a newer edit exists
- **THEN** the change is rejected with an actionable explanation and no existing assignment is silently overwritten

### Requirement: Organize ticket detail
The detail SHALL visually distinguish the ticket description and response editor while keeping identifier, receipt date and classification tags readily discoverable. Classification provenance SHALL remain accessible without a prominent model suggestions section.

#### Scenario: Inspect a ticket
- **WHEN** an operator opens its detail
- **THEN** the subject and tags precede the description and the response has a distinct, visually emphasized container
