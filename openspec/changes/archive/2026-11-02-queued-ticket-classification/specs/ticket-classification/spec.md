## Purpose

Provide durable background ticket classification with observable simulated results and recoverable failures.

## ADDED Requirements

### Requirement: Process pending classification
The system SHALL process pending classification jobs asynchronously and persist their status and result.

#### Scenario: Worker completes classification
- **WHEN** a worker processes a pending ticket classification
- **THEN** it stores a fixed domain-neutral result identified as simulated
- **AND** marks the job completed

#### Scenario: Worker unavailable
- **WHEN** a ticket is created while the worker is stopped
- **THEN** its job remains pending and can be processed after the worker starts

### Requirement: Recover and retry classification jobs
The system SHALL recover abandoned jobs and retry failures a bounded number of times with a delay before recording final failure.

#### Scenario: Worker stops during processing
- **WHEN** a worker stops before completing a claimed job
- **THEN** the job becomes eligible for recovery after its claim expires
- **AND** stale workers cannot overwrite a newer claim's result

#### Scenario: Attempts exhausted
- **WHEN** all automatic attempts fail
- **THEN** the job becomes failed and the ticket remains available

#### Scenario: Job is retried
- **WHEN** a job is processed more than once due to recovery or retry
- **THEN** at most one current classification result is visible for the ticket

### Requirement: Retry failed classification
The system SHALL allow an operator to request a new processing attempt after automatic attempts are exhausted.

#### Scenario: Manual retry requested
- **WHEN** an operator retries a failed classification
- **THEN** the system queues it for a new bounded sequence of attempts

#### Scenario: Repeated retry requests
- **WHEN** retry requests for the same ticket occur concurrently or repeatedly
- **THEN** at most one active classification job exists for that ticket
