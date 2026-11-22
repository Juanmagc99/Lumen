# backend-observability Specification

## Purpose

Provide consistent, safe operational diagnostics for API and worker processes.

## Requirements

### Requirement: Shared operational logging
The API, worker and server SHALL use a shared configurable logging level and emit structured operational events to standard error.

#### Scenario: Process reports an event
- **WHEN** the API or worker emits an operational event at the configured level
- **THEN** the event includes a timestamp, severity, process and event name

#### Scenario: Server reports an event
- **WHEN** the server emits an enabled operational event
- **THEN** the event uses the same structured fields as Lumen events

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
- **THEN** its existing HTTP status and recovery semantics are preserved and the response uses the uniform error contract

### Requirement: Worker failure diagnostics
The worker SHALL record the operation and exception type for unexpected polling or processing failures while preserving its retry behavior.

#### Scenario: Worker operation fails
- **WHEN** a worker loop encounters an unexpected exception
- **THEN** it records a safe failure event and retries according to its existing delay

### Requirement: Shared error catalogue
The API and worker SHALL classify errors using a shared catalogue of stable codes and safe messages, using specific codes where recovery differs and general codes otherwise.

#### Scenario: Actionable conflict
- **WHEN** a request fails because its revision is stale
- **THEN** the catalogue identifies the stale revision separately from unrelated conflicts

#### Scenario: Worker failure
- **WHEN** a new worker job fails with a known cause
- **THEN** the persisted failure identifies a catalogue code appropriate to that cause

### Requirement: Uniform API errors
API error responses SHALL use a consistent JSON contract containing a stable error code, a safe message and the server-generated request identifier.

#### Scenario: Expected error response
- **WHEN** validation, authentication, authorization, conflict or storage handling rejects a request
- **THEN** the response uses the common contract and the corresponding HTTP status

#### Scenario: Unexpected error response
- **WHEN** an unexpected failure occurs
- **THEN** the response uses a generic catalogue code and message without exposing exception details

#### Scenario: Browser recovery
- **WHEN** the SPA receives a catalogue error
- **THEN** it retains the appropriate session, permission, conflict or retry behavior

### Requirement: Historical worker failure compatibility
The system SHALL keep existing stored worker failure values unchanged and translate recognized historical values into safe, meaningful output.

#### Scenario: Existing job is viewed
- **WHEN** a historical job has a recognized legacy code or failure message
- **THEN** its failure remains understandable alongside new catalogue-coded failures

#### Scenario: Unknown historical value
- **WHEN** a historical failure value is not recognized
- **THEN** the system displays a generic safe failure message without exposing the stored value

### Requirement: Safe allowlisted operational events
Lumen SHALL emit only defined operational events and permitted field values; rejected events or fields SHALL be omitted and produce a safe warning without interrupting the operation.

#### Scenario: Unapproved data is supplied
- **WHEN** an event or field is not approved or its value is invalid
- **THEN** the unapproved data is not recorded and a warning excludes the rejected value

### Requirement: Safe HTTP access events
The API SHALL record each completed HTTP request with method, safe route template, response status, duration and request identifier.

#### Scenario: Request contains identifiers or query data
- **WHEN** an HTTP request is processed
- **THEN** its access event excludes raw paths, path values, query strings and request content

#### Scenario: Request has no matched route
- **WHEN** the request does not match a route or is rejected before routing
- **THEN** the access event uses a fixed fallback route marker without recording the raw path

### Requirement: External library log level
Third-party library logs SHALL default to warning severity or higher, without treating their messages as Lumen allowlisted events.

#### Scenario: External informational message
- **WHEN** a third-party library emits an informational message with default configuration
- **THEN** that message is not emitted
