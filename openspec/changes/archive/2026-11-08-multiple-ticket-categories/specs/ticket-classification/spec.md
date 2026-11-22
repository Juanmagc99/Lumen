## MODIFIED Requirements

### Requirement: Process pending classification
The system SHALL process pending classification jobs asynchronously using a configurable decision model and persist their status and validated result. Each completed real result SHALL contain zero or more distinct active categories and at most one active priority. An empty category list and an undetermined priority SHALL represent insufficient evidence for their respective dimensions.

#### Scenario: Worker completes classification
- **WHEN** a worker processes a pending ticket classification and receives a valid decision
- **THEN** it stores the selected categories and priority or explicit undetermined values
- **AND** identifies the result as model-generated and marks the job completed

#### Scenario: Worker unavailable
- **WHEN** a ticket is created while the worker is stopped
- **THEN** its job remains pending and can be processed after the worker starts

#### Scenario: Invalid or unavailable decision
- **WHEN** the provider fails, refuses, times out, or returns an invalid, duplicate, wrong-kind, or inactive option
- **THEN** no invented or simulated result is recorded as a real decision
- **AND** the existing bounded failure and retry policy applies

#### Scenario: No active options
- **WHEN** a required option list has no active values
- **THEN** the job is not reported as successfully classified
- **AND** its failure is visible and recoverable through the retry policy

#### Scenario: Untrusted ticket content
- **WHEN** ticket content contains instructions that conflict with the classification task
- **THEN** the content is treated as data and cannot authorize application actions

#### Scenario: Historical simulated result
- **WHEN** a ticket has a previously completed simulated result
- **THEN** it remains identified as simulated and is not presented as a real model decision

### Requirement: Preserve manual classification choices
A manually chosen category set or priority SHALL take precedence over automated results for that field, including results already in progress or produced after retry. The other field SHALL remain eligible for automatic classification until manually chosen. A manually saved empty category set SHALL remain a manual choice.

#### Scenario: Model completes after manual edit
- **WHEN** an operator changes a field while classification is processing and the worker completes
- **THEN** the manual value remains the current value and the other field can receive the valid model result
- **AND** the model's category suggestions remain separately inspectable

#### Scenario: Retry after manual edit
- **WHEN** classification is retried after a field was manually changed
- **THEN** the manual field remains unchanged

#### Scenario: Operator clears categories
- **WHEN** an operator saves an empty category selection
- **THEN** the selection remains empty even if a model result arrives later

### Requirement: Retain classification provenance
The application SHALL distinguish current manual choices from model-generated and historical simulated results without presenting simulated results as real model decisions. Model category suggestions SHALL remain separately inspectable when a manual category set takes precedence.

#### Scenario: Inspect origin
- **WHEN** an operator inspects classification provenance
- **THEN** the origin of current values and any available historical simulated result are clearly identified
- **AND** the latest available model category suggestions are distinguishable from the effective manual selection

## ADDED Requirements

### Requirement: Preserve existing category assignments
The system SHALL retain existing manual and automated category assignments, their provenance, and option identity when upgrading to multiple categories.

#### Scenario: Upgrade an existing ticket
- **WHEN** a ticket with an existing category is migrated
- **THEN** the corresponding category is retained in the appropriate category collection
- **AND** its effective selection and origin remain unchanged
