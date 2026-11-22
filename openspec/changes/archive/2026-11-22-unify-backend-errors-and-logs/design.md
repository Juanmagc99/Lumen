# Design

## Context

See the proposal. HTTP errors currently arise from route handlers, request validation and security middleware. Classification stores short reason codes, while knowledge jobs also store human-readable legacy failures. The SPA uses HTTP status, `detail` and these job values for recovery and presentation.

## Goals / Non-Goals

**Goals:** A predictable error contract, meaningful historical failures and safe, correlated diagnostics across API, worker and Uvicorn.

**Non-Goals:** Browser telemetry, a remote logging platform, rewriting historical database rows or guaranteeing third-party messages are sanitized.

## Decisions

1. Define an application-owned catalogue with stable uppercase codes, safe messages, applicable status and recovery semantics. Map explicit domain errors at inbound boundaries, including security and validation, rather than matching arbitrary exception text. Use distinct stale-revision and queue-full codes where recovery differs and generic categories where it does not. Keep framework-specific status handling at the HTTP boundary.
2. Return `{ "error": { "code": "...", "message": "...", "request_id": "..." } }` for every application-controlled HTTP error, with the same ID in `X-Request-ID`. Preserve existing status codes, security restrictions and special headers such as `Retry-After` where present. Unknown errors receive a generic 500. Update the SPA in the same release, retaining conflict reload, session and permission behavior. External clients must adopt the new envelope.
3. Persist catalogue codes for newly recorded classification, ingestion, semantic-index and generation failures, respecting existing column limits. Translate the known legacy codes and messages at the read boundary without updating historical rows. Map unknown historical values to a generic safe failure, never echo them. Keep retry and lease semantics unchanged.
4. Replace free-form Lumen event messages with an event registry and per-event field schemas. Validate values as well as names: use enums, numeric types, generated IDs and approved route templates rather than arbitrary strings. A rejected event or field emits a fixed safe warning without the rejected value; avoid recursive logging and never fail the caller. Apply the guard at the handler boundary too, so direct logger use cannot bypass it.
5. Use shared JSON serialization for API, worker and Uvicorn lifecycle/error events, sanitizing or replacing untrusted server messages. Suppress Uvicorn's default access formatter and emit one request-completion event from the API boundary, including a route template or fixed unmatched marker, no raw paths or query strings, status, duration and generated request ID. The access event is emitted independently of the ordinary severity threshold so every completed request is represented; preserve configurable filtering for other events. Avoid duplicate access records.
6. Configure third-party library loggers to warning by default while keeping their own format and treating their output as potentially sensitive. Do not claim warning level provides redaction. Avoid changing external dependency behavior beyond logging configuration.

## Risks / Trade-offs

- [The response envelope breaks existing clients] -> Document the schema and coordinate API and SPA deployment; preserve status and recovery semantics.
- [A logger or Uvicorn traceback leaks untrusted text] -> Use fixed safe server events and reject arbitrary values at the handler, including exception messages and tracebacks.
- [Historical values do not map cleanly] -> Inventory current storage values and document the generic fallback without modifying source records.
- [Access events increase volume] -> Emit compact records without request bodies; manage retention outside this change.
- [Third-party warnings may include sensitive content] -> Document this limit and restrict access to log output; no complete redaction guarantee is made.

## Migration Plan

Deploy API, worker and SPA together after backing up data. New worker codes must fit the existing schema; old values remain readable. On rollback, restore matching API, worker and SPA versions and ensure newly persisted codes are translated for the older version before resuming it; do not rewrite historical records as part of the forward deployment.
