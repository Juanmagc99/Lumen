## ADDED Requirements

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
