# Spec Delta

## MODIFIED Requirements

### Requirement: Display classification progress
The API and SPA SHALL expose classification status for each ticket and the detail SHALL expose its available category, priority, and result source, including explicit undetermined values and historical simulated results.

#### Scenario: Ticket is pending or processing
- **WHEN** classification is pending or processing
- **THEN** its status is visible in the list and detail without presenting a completed result

#### Scenario: Classification is complete
- **WHEN** classification completes
- **THEN** the list and detail show completed status
- **AND** the detail shows category and priority or their undetermined states and identifies the result source

#### Scenario: Classification fails
- **WHEN** automatic attempts are exhausted
- **THEN** the list and detail show failed status and the detail explains that retry is available

## ADDED Requirements

### Requirement: Filter by category and priority
The API and inbox SHALL support category and priority filters combined with existing filters before counting and pagination.

#### Scenario: Combined classification filters
- **WHEN** category and priority filters are supplied with other filters
- **THEN** only tickets matching all supplied filters are counted and returned

#### Scenario: Historical option is inactive
- **WHEN** an operator filters by an inactive option associated with existing tickets
- **THEN** those tickets remain discoverable
