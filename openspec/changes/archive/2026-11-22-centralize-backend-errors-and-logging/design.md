# Design

## Context

The API already has selected exception handlers and the worker has independent retry loops. Existing job failure records and HTTP contracts must remain intact.

## Goals / Non-Goals

**Goals:** Shared diagnostics with safe fields, request correlation and predictable unexpected-error responses.

**Non-Goals:** Browser telemetry, external log services, persistent audit logs, or changes to business retries and existing expected HTTP errors.

## Decisions

- Use Python standard logging with a JSON formatter and `LUMEN_LOG_LEVEL` for Lumen loggers. Do not reconfigure third-party logging, which can have separate privacy properties. This avoids a new dependency and preserves server logging configuration.
- Emit only fixed event names and allowlisted context, never exception text or tracebacks. This sacrifices detailed stacks to prevent leakage from untrusted inputs and provider errors.
- Install request correlation and an unexpected exception boundary at the HTTP layer. Generate identifiers locally instead of trusting request headers. Keep existing handlers and `detail` conventions.
- Replace generic worker warnings with shared safe exception events, retaining all current loop delays and job records. Do not log user data or job payloads.

## Risks / Trade-offs

- [Limited diagnostics without exception messages] -> Record exception class and operation, retaining safe correlation for investigation.
- [Third-party server logs are outside the shared policy] -> Document this boundary and avoid claiming complete redaction of external logging.

## Migration Plan

Restart API and worker to use the shared logging configuration. Roll back by restoring prior application code; no data migration is needed.
