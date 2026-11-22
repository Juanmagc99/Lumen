# Proposal

## Why

Lumen cannot yet receive or retain tickets, so there is no real ticket journey to inspect. A persisted intake and read-only inbox provide the foundation for later processing without coupling receipt to a queue or model.

## What Changes

- Accept tickets through an HTTP API, persist them in PostgreSQL, and expose list and detail endpoints.
- Support an optional client-provided idempotency key for safe retries and reject conflicting reuse.
- Provide a read-only SPA inbox ordered by most recent receipt and a ticket detail view.
- Add local PostgreSQL through Docker Compose, asynchronous SQLAlchemy access using asyncpg, and versioned Alembic migrations.
- Document setup, usage, limitations, and the actual checks performed.

## Capabilities

### New Capabilities

- `ticket-intake`: Validated, durable ticket creation and idempotent retries through the API.
- `ticket-browsing`: Read-only ticket listing and detail through the API and SPA.

### Modified Capabilities

None. The existing process-only health check remains unchanged.

## Impact

The FastAPI application, SPA, local development configuration, dependencies, and documentation are affected. PostgreSQL becomes necessary for ticket operations. Queueing, classification, AI, ticket editing, deletion, and outbound messages remain outside this change.
