## MODIFIED Requirements

### Requirement: Intake is independent of processing
Ticket creation SHALL atomically persist a pending classification job with the ticket and SHALL NOT depend on a running worker, classification, or model provider.

#### Scenario: No processing services configured
- **WHEN** a valid ticket is submitted with only the API and its database available
- **THEN** the API persists the ticket and its pending job without claiming a processing result

#### Scenario: Atomic handoff fails
- **WHEN** the ticket or its pending job cannot be persisted
- **THEN** neither is committed and the API does not report successful creation

#### Scenario: Idempotent creation replay
- **WHEN** an existing ticket creation is replayed with the same idempotency key and content
- **THEN** the API returns the original ticket without creating another classification job
