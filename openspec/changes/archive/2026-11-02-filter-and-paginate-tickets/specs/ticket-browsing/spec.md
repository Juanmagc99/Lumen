# Spec Delta

## MODIFIED Requirements

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

## ADDED Requirements

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
