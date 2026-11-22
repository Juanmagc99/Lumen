# Proposal

## Why

Backend error responses and persisted job failures use inconsistent representations, while operational logging does not enforce its privacy policy on future events. A common error catalogue and controlled logging make failures actionable and diagnostics consistent across the API and worker.

## What Changes

- **BREAKING**: Adopt a uniform API error response with a stable catalogue code, safe message and request identifier; update the SPA to use the new contract and preserve appropriate recovery behavior.
- Define shared error codes for the API and worker, with specific codes where they enable different recovery actions and general codes otherwise.
- Record new worker failures using catalogue codes and translate historical failure values when presenting them, without rewriting stored historical records.
- Use a common structured format for Lumen API, worker and Uvicorn events. Record each HTTP access with method, safe route template, status, duration and request identifier, excluding raw paths, query strings and request content.
- Restrict Lumen operational events and fields to an explicit allowlist; discard unapproved values and emit a safe warning without interrupting application operations.
- Default third-party library loggers to warning or higher, without claiming their messages are covered by Lumen's event safety policy.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `backend-observability`: Define a shared error catalogue, uniform error responses, safe allowlisted logging, Uvicorn integration and historical worker failure compatibility.

## Impact

The API error contract changes for clients, including the SPA. API middleware, HTTP adapters, worker job processing, persisted failure presentation, logging configuration, the development launcher and operational documentation are affected. Existing status codes and recovery semantics should be retained where possible. The browser is updated only to consume errors and historical failure values; browser telemetry is outside scope. No external logging service is required.
