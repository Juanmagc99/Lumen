# Spec Delta

## MODIFIED Requirements

### Requirement: Process pending classification
The system SHALL process pending classification jobs asynchronously using a configurable decision model and persist their status and validated result. Each completed real result SHALL contain at most one active category and one active priority, each independently permitted to be undetermined when evidence is insufficient.

#### Scenario: Worker completes classification
- **WHEN** a worker processes a pending ticket classification and receives a valid decision
- **THEN** it stores the selected category and priority or explicit undetermined values
- **AND** identifies the result as model-generated and marks the job completed

#### Scenario: Worker unavailable
- **WHEN** a ticket is created while the worker is stopped
- **THEN** its job remains pending and can be processed after the worker starts

#### Scenario: Invalid or unavailable decision
- **WHEN** the provider fails, refuses, times out, or returns an invalid or inactive option
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
