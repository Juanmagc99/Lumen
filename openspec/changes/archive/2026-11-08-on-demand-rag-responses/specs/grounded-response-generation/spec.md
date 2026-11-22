# Spec Delta

## Purpose

Generate auditable, evidence-grounded ticket response suggestions on explicit operator request.

## ADDED Requirements

### Requirement: Request generation explicitly
The system SHALL request generation only through an explicit operator action on a ticket using the independently configured response model, with either a selected knowledge base or an explicit choice to proceed without one.

#### Scenario: Request a suggestion
- **WHEN** an operator selects a knowledge base and requests generation
- **THEN** a durable generation job is created and the response editor remains available

#### Scenario: Request without a knowledge base
- **WHEN** an operator chooses generation without a base
- **THEN** the system uses ticket information and may offer general suggestions, identifies missing specific facts, does not fabricate citations, and visibly states that no sources were consulted
- **AND** the suggestion remains subject to human review and is never automatically sent

#### Scenario: Duplicate request
- **WHEN** repeated or concurrent requests target a ticket with an active generation job
- **THEN** at most one active generation exists for that ticket and the existing job is returned or identified

### Requirement: Show durable job progress
The system SHALL expose queued, running, completed, and failed generation states and allow a failed request to be retried.

#### Scenario: Worker interruption
- **WHEN** a worker stops during a job
- **THEN** the job can be recovered and an expired claim cannot overwrite a newer result

#### Scenario: Attempts exhausted
- **WHEN** bounded attempts fail
- **THEN** the failure is visible and the operator can request a new attempt

### Requirement: Apply shared request limits
The system SHALL enforce configurable shared concurrency and time-based request limits across workers for response model calls, including retries.

#### Scenario: Capacity exhausted
- **WHEN** a job is ready but a limit is reached
- **THEN** it remains queued until capacity is available without issuing a model call

### Requirement: Retrieve scoped evidence
The system SHALL retrieve only ready, active content from the selected knowledge base and make cited document versions and relevant excerpts inspectable.

#### Scenario: Inspect a citation
- **WHEN** an operator inspects a generated suggestion's citation
- **THEN** the cited document identity, version, and excerpt are available even after a later document update

### Requirement: Handle insufficient evidence
The system SHALL explicitly indicate insufficient evidence and instruct the model not to present unsupported claims or fabricated citations as established facts; human review remains necessary because model output can be incorrect.

#### Scenario: No useful evidence
- **WHEN** retrieval provides insufficient support for an answer
- **THEN** the result identifies the limitation for human review instead of inventing a supported answer

### Requirement: Validate source references
The system SHALL validate generated citation references against the evidence actually retrieved and SHALL treat tickets and documents as untrusted data.

#### Scenario: Invalid citation or embedded instruction
- **WHEN** output references an unknown source or source content asks the model to override its task
- **THEN** the invalid reference is not accepted as a verified citation and the embedded instruction cannot authorize application actions

### Requirement: Retain generation audit
The system SHALL retain each generation request and attempt with status, timestamps, model and provider, configuration version, retrieved source versions, outcome, and a concise evidence-based rationale where available.

#### Scenario: Failed or successful attempt
- **WHEN** an attempt finishes or fails
- **THEN** its available diagnostics remain inspectable without exposing credentials

### Requirement: Record usage and estimated cost
The system SHALL record reported token usage and provider usage identifiers when available, and estimated cost with currency and pricing basis when calculable; unavailable values SHALL remain explicitly unknown.

#### Scenario: Usage unavailable
- **WHEN** a provider does not report usage or a price is unavailable
- **THEN** the audit shows the affected values as unknown rather than zero or invented credits

### Requirement: Preserve generated output
The system SHALL store every completed generation's original AI text independently of the editable visible response and retain it when that response is edited or approved.

#### Scenario: Multiple suggestions
- **WHEN** an operator generates another suggestion and edits the visible response
- **THEN** each completed original remains separately identifiable and unchanged
