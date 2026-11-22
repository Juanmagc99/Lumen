## MODIFIED Requirements

### Requirement: Display classification progress
The API and SPA SHALL expose classification status for each ticket and the detail SHALL expose its available categories, priority, and result source, including explicit undetermined values and historical simulated results.

#### Scenario: Ticket is pending or processing
- **WHEN** classification is pending or processing
- **THEN** its status is visible in the list and detail without presenting a completed result

#### Scenario: Classification is complete
- **WHEN** classification completes
- **THEN** the list and detail show completed status
- **AND** the detail shows categories and priority or their undetermined states and identifies the result source

#### Scenario: Classification fails
- **WHEN** automatic attempts are exhausted
- **THEN** the list and detail show failed status and the detail explains that retry is available

### Requirement: Filter by category and priority
The API and inbox SHALL support category and priority filters combined with existing filters before counting and pagination. A ticket matches a category filter when any effective category matches the selected value.

#### Scenario: Combined classification filters
- **WHEN** category and priority filters are supplied with other filters
- **THEN** only tickets matching all supplied filters are counted and returned

#### Scenario: Historical option is inactive
- **WHEN** an operator filters by an inactive option associated with existing tickets
- **THEN** those tickets remain discoverable

### Requirement: Present ticket tags
The inbox and detail SHALL present all current categories and the current priority as named colored tags. The detail SHALL place them near the top in separate category and priority rows.

#### Scenario: Classified ticket
- **WHEN** a ticket has categories and a priority
- **THEN** all their names and configured colors are visible in the list and detail

#### Scenario: Missing or inactive value
- **WHEN** a value is undetermined or its option has been deactivated
- **THEN** the detail identifies that state without inventing a value and existing inactive associations remain visible

### Requirement: Edit ticket tags
The detail SHALL allow an operator to replace the complete category selection and select a priority independently, save changes, and see their current values in the list and detail. It SHALL report errors and reject stale writes without silently replacing newer choices. Existing inactive categories can be retained or removed but cannot be newly selected.

#### Scenario: Change a tag
- **WHEN** an operator selects and saves active options of the correct type
- **THEN** the selection persists and filters use the current assignment

#### Scenario: Invalid or stale selection
- **WHEN** a newly selected option is inactive, has the wrong type, or a newer edit exists
- **THEN** the change is rejected with an actionable explanation and no existing assignment is silently overwritten

#### Scenario: Retain an inactive category
- **WHEN** an operator edits a ticket with an existing inactive category
- **THEN** the operator can retain or remove that category while changing other categories

## ADDED Requirements

### Requirement: Expose category collections
Ticket list and detail responses SHALL expose effective and model category collections, and category edits SHALL accept a complete collection with a revision. A saved empty manual collection SHALL be distinguishable from no manual choice.

#### Scenario: Review model and manual categories
- **WHEN** a ticket has model suggestions and a manual selection
- **THEN** clients can distinguish the effective manual categories from the model suggestions

#### Scenario: Multiple filter matches
- **WHEN** a ticket matches more than one selected category
- **THEN** it appears once in the result and contributes once to the total
