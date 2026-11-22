# Tasks

## 1. Error catalogue and API contract

- [x] 1.1 Define the shared catalogue, safe messages and mappings for current API and worker causes; inspect mappings for distinct stale-revision and queue-full recovery and existing storage limits.
- [x] 1.2 Centralize error responses across HTTP routes, validation, security and unexpected failures; inspect status codes, headers, safe messages and request ID correlation for each boundary.
- [x] 1.3 Update SPA error handling for the new envelope and preserve session, permission, conflict and retry flows; manually inspect representative flows using fictional data.
- [x] 1.4 Document the error contract, catalogue and coordinated API/SPA deployment and rollback; compare examples with the final implementation.

## 2. Worker failure compatibility

- [x] 2.1 Record catalogue codes for new classification, ingestion, semantic-index and generation failures without changing retries; inspect all write paths and field lengths.
- [x] 2.2 Translate legacy codes and stored messages at read boundaries, including a safe unknown fallback; inspect representative historical and new values without rewriting historical rows.
- [x] 2.3 Document legacy handling and rollback for newly stored codes; verify the steps against the supported versions and field mappings.

## 3. Structured logging

- [x] 3.1 Implement an event registry and handler-level validation of event names and field values; inspect that rejected values are omitted and warnings cannot interrupt or recurse.
- [x] 3.2 Unify Lumen and Uvicorn lifecycle/error output, suppress duplicate default access logs and configure third-party logging defaults; inspect configuration and privacy boundaries.
- [x] 3.3 Emit one safe HTTP access event per completed request with route template or fixed fallback, status, duration and request ID; inspect matched, unmatched and security-rejected requests without exposing raw paths or queries.
- [x] 3.4 Document log fields, filtering, unconditional access events and third-party limitations; compare the instructions with actual configuration.

## 4. Integration

- [x] 4.1 Validate the change and perform appropriate manual API, worker and SPA checks using fictional data, including sensitive-data exclusion and historical compatibility; report what was and was not exercised without creating or running tests.
