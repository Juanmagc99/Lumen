# ticket-browsing Specification

## Purpose

Let operators inspect received tickets through a read-only API and web inbox.

## Requirements

### Requirement: List tickets
The API SHALL return a bounded page of persisted tickets ordered by receipt timestamp descending, with identifier descending as a deterministic tie-breaker. Each entry SHALL include its identifier, subject, receipt timestamp, and classification status. The response SHALL include the requested page, page size, and total matching tickets.

#### Scenario: Tickets exist
- **WHEN** a client requests the ticket list without filters
- **THEN** the response contains the first page of persisted tickets with the most recently received first

#### Scenario: No tickets exist
- **WHEN** a client requests the ticket list and no tickets exist
- **THEN** the API returns an empty page and a total of zero

#### Scenario: Page beyond the available results
- **WHEN** a valid page number exceeds the number of matching pages
- **THEN** the API returns an empty page with the matching total

### Requirement: Retrieve a ticket
The API SHALL return a ticket's identifier, subject, description, and receipt timestamp when requested by its identifier.

#### Scenario: Existing ticket
- **WHEN** a client requests an existing ticket
- **THEN** the API returns the stored ticket data

#### Scenario: Unknown ticket
- **WHEN** a client requests a well-formed identifier that does not match a ticket
- **THEN** the API returns HTTP 404

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

### Requirement: Filter tickets
The API SHALL combine optional title text, classification status, and receipt date range filters before pagination and counting. Title matching SHALL be case-insensitive literal substring matching. Date bounds SHALL be inclusive UTC calendar dates.

#### Scenario: Combined filters
- **WHEN** a client supplies multiple filters
- **THEN** only tickets satisfying all supplied filters are counted and eligible for the returned page

#### Scenario: Search text contains wildcard characters
- **WHEN** a client searches for text containing percent or underscore characters
- **THEN** those characters are matched literally in the title

#### Scenario: Date boundaries
- **WHEN** a client supplies a start or end date
- **THEN** tickets received on that UTC calendar date are included at that boundary

#### Scenario: Invalid filters
- **WHEN** a date is invalid, the start date is after the end date, or a classification status is unsupported
- **THEN** the API rejects the request with a validation error

### Requirement: Bound pagination inputs
The API SHALL default to page 1 with 25 items per page and accept positive page numbers and page sizes from 1 through 100.

#### Scenario: Invalid pagination
- **WHEN** the page number or size is outside the allowed range
- **THEN** the API rejects the request with a validation error

### Requirement: Browse filtered pages
The inbox SHALL provide accessible controls for title, classification status, receipt date range, page navigation, and page sizes of 25, 50, 75, and 100. It SHALL distinguish an empty inbox from no matching results and allow filters to be cleared.

#### Scenario: Change page size
- **WHEN** an operator selects a page size
- **THEN** the inbox displays the first page at the selected size while retaining applied filters

#### Scenario: Apply filters
- **WHEN** an operator applies or clears filters
- **THEN** the inbox displays the first page of the resulting list

#### Scenario: Return from details
- **WHEN** an operator opens a ticket and returns to the inbox
- **THEN** the applied filters, page size, and page are restored

#### Scenario: Results change while browsing
- **WHEN** a previously valid page becomes empty because matching tickets changed
- **THEN** the inbox returns to the last available page, or page one if there are no matches

#### Scenario: No matching tickets
- **WHEN** filters match no tickets
- **THEN** the inbox explains that no tickets match and provides a way to clear the filters

### Requirement: Filter by multiple classification values
The API and inbox SHALL accept multiple classification statuses, categories, and priorities. Values within a dimension match any selected value; different dimensions and other filters combine before counting and pagination.

#### Scenario: Multiple values and dimensions
- **WHEN** two categories and two priorities are selected
- **THEN** matching tickets have any selected category and any selected priority

#### Scenario: No values selected
- **WHEN** no values are selected for a dimension
- **THEN** that dimension does not restrict results

#### Scenario: Inactive historical options
- **WHEN** an inactive category or priority associated with existing tickets is selected among other values
- **THEN** matching historical tickets remain discoverable

#### Scenario: Legacy requests and invalid values
- **WHEN** a client uses existing single-value parameters
- **THEN** they retain their existing filtering behavior
- **AND** unsupported statuses and malformed identifiers are rejected

### Requirement: Present and retain filter selections
The inbox SHALL provide custom multi-selection controls for status, category, and priority, show applied selections, and allow individual selections or all filters to be cleared.

#### Scenario: Apply and remove selections
- **WHEN** an operator applies multiple values and then removes one applied value
- **THEN** the remaining selections are retained and the updated results begin on page one

#### Scenario: Return to a filtered inbox
- **WHEN** an operator opens a ticket and returns to the inbox
- **THEN** all applied selections, date bounds, search text, page size, and page are restored

#### Scenario: Restore an existing inbox link
- **WHEN** an operator opens an existing single-value filtered inbox URL
- **THEN** the corresponding selections and results are restored

### Requirement: Group receipt dates and pagination controls
The inbox SHALL present the receipt start and end dates together with matching field sizes and place the page-size control with pagination.

#### Scenario: Adjust receipt range
- **WHEN** an operator views the date range
- **THEN** both date bounds are adjacent at widths that allow it and remain grouped when stacked
- **AND** their inclusive UTC meaning and validation are clear

#### Scenario: Change page size
- **WHEN** an operator changes page size
- **THEN** the first page is shown with the applied filters retained

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

### Requirement: Organize ticket detail
The detail SHALL visually distinguish the ticket description and response editor while keeping identifier, receipt date and classification tags readily discoverable. Classification provenance SHALL remain accessible without a prominent model suggestions section.

#### Scenario: Inspect a ticket
- **WHEN** an operator opens its detail
- **THEN** the subject and tags precede the description and the response has a distinct, visually emphasized container

### Requirement: Expose category collections
Ticket list and detail responses SHALL expose effective and model category collections, and category edits SHALL accept a complete collection with a revision. A saved empty manual collection SHALL be distinguishable from no manual choice.

#### Scenario: Review model and manual categories
- **WHEN** a ticket has model suggestions and a manual selection
- **THEN** clients can distinguish the effective manual categories from the model suggestions

#### Scenario: Multiple filter matches
- **WHEN** a ticket matches more than one selected category
- **THEN** it appears once in the result and contributes once to the total
