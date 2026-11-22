# Backend observability

## Purpose

Provide consistent, safe operational diagnostics for API and worker processes.

## ADDED Requirements

### Requirement: Shared operational logging
The API and worker SHALL use a shared configurable logging level and emit structured operational events to standard error.

#### Scenario: Process reports an event
- **WHEN** the API or worker emits an operational event at the configured level
- **THEN** the event includes a timestamp, severity, process and event name

### Requirement: Safe diagnostic data
Operational events SHALL exclude credentials, request and response bodies, ticket and document content, provider payloads and exception messages.

#### Scenario: Unexpected exception contains sensitive text
- **WHEN** an unexpected exception is logged
- **THEN** the event reports its exception type and safe execution context without its message or traceback

### Requirement: API error correlation
The API SHALL assign a server-generated request identifier, return it in the response header, and use it to correlate unexpected error events with a generic HTTP 500 response.

#### Scenario: Unexpected request failure
- **WHEN** a request fails unexpectedly
- **THEN** the response contains a generic error and request identifier, and a matching safe error event is recorded

#### Scenario: Expected request failure
- **WHEN** an existing validation, authentication, domain or storage error occurs
- **THEN** its existing HTTP status and response semantics are preserved

### Requirement: Worker failure diagnostics
The worker SHALL record the operation and exception type for unexpected polling or processing failures while preserving its retry behavior.

#### Scenario: Worker operation fails
- **WHEN** a worker loop encounters an unexpected exception
- **THEN** it records a safe failure event and retries according to its existing delay
