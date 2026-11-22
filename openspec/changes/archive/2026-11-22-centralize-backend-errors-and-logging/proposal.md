# Proposal

## Why

API errors and worker logs use fragmented handling, making failures difficult to diagnose consistently and safely.

## What Changes

- Configure a shared, structured operational logging policy for the API and worker.
- Centralize unexpected HTTP error handling and request correlation while preserving existing expected error responses.
- Record safe, contextual worker failures without leaking request, ticket, document, provider, or credential contents.
- Document configuration and log inspection.

## Capabilities

### New Capabilities

- `backend-observability`: Safe operational logging and error handling for API and worker processes.

### Modified Capabilities

None.

## Impact

API bootstrap, worker runner, shared backend configuration and development documentation. No additional service or dependency is required. The browser is outside scope.
