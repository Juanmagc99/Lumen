# Design

## Context

Ticket creation currently commits to PostgreSQL with an optional idempotency key; no worker exists. Intake must remain available without a worker. The database volume can be shared across checkouts. See the proposal and capability deltas for scope and behavior.

## Goals / Non-Goals

**Goals:** durable asynchronous handoff, observable processing, safe retries, and consistent local database configuration.

**Non-Goals:** external messaging, real model inference, profiles, retrieval, response generation, or advanced filters.

## Decisions

1. Use a PostgreSQL-backed job table as the queue. Insert the ticket, idempotency association, and one pending classification job in the same transaction. A replay returns the existing ticket and creates no job. A database queue is sufficient for this scope; an external broker would need an additional transactional outbox relay. The atomic handoff follows the same transaction principle as outbox, but directly consuming jobs is not a classical event-publishing outbox.
2. Run a separate worker with bounded database sessions. Atomically claim an eligible job using row locking with `SKIP LOCKED`, a unique claim token, attempt count, and expiry. Commit the claim before processing; never hold a database transaction open during processing. Complete or fail only if the token is still current. Recover expired claims within the same bounded attempt policy; stale workers cannot publish results. Enforce at most one active job per ticket in the database. A duplicate execution is possible, so commit the result and job completion atomically and retain at most one current result per ticket.
3. Use a domain-neutral fixed simulated result with an explicit source marker. Default to three attempts per cycle with a ten-second delay and a two-minute claim expiry, configurable as operational settings; count a recovered abandoned claim as an attempt. Once exhausted, mark failed. A manual retry atomically starts a fresh bounded cycle only for a failed job; repeated or concurrent requests must not create duplicate active work. Return a clear conflict or current status when retry is not applicable. Do not expose exception details or ticket contents in logs.
4. Expose status in list and detail and the simulated result in detail. Provide a retry action on failed detail with pending and error feedback; refresh status without creating duplicate requests. Keep a domain-facing classifier boundary so a separately configurable decision model can replace simulation later. No automated response generation is triggered.
5. Accept database user, password, database name, and host port from root `.env` via the existing safe loader, with consistent settings for Compose, API, migrations, and worker. PostgreSQL retains its internal container port. Construct connection URLs using a structured URL builder or correct escaping; never log credentials. Keep `.env` ignored and provide a credential-free example. Existing PostgreSQL initialization settings apply only to a new volume; changing `.env` does not alter existing roles, passwords, or databases. Validate or document mismatch and avoid silently resetting the volume. Manage worker start, stop, restart, status, and logs alongside existing processes, respecting shared services and process identity.
6. Centralize backend environment reading, validation, defaults, and typed settings in a shared configuration module consumed by the API database layer, migrations, and worker. Preserve `DATABASE_URL` precedence for manual sessions and the existing environment-based launch behavior; loading `.env` remains the development script's responsibility, and Compose retains its own infrastructure configuration. Validate settings only where needed so process liveness remains independent of database configuration. Avoid introducing a dependency solely for configuration.

## Risks / Trade-offs

- [A worker dies after starting an attempt] -> Lease expiry and claim fencing permit safe recovery; external inference in a future change may still incur duplicate cost.
- [A shared local database is mistaken for disposable data] -> Inspect the actual configured target and sharing before any one-time cleanup; clear only Lumen data, retain schema and volume, and report the outcome.
- [A developer changes `.env` against an initialized volume] -> Explain initialization semantics and fail visibly on connection mismatch; do not recreate data automatically.
- [Polling delays status updates] -> Refresh visible status with bounded polling and stop on navigation; no real-time infrastructure is needed.

## Migration Plan

Inspect the configured local database and its sharing, stop managed writers, and perform the explicitly requested one-time deletion of Lumen data while retaining structure and volume. If the target cannot be identified safely, stop before deletion. Apply a versioned migration for jobs and results, configure the local credentials, and start the services. New tickets acquire jobs atomically; old tickets are not backfilled because their deletion is requested. Document rollback and retain data unless explicitly authorized for deletion. Do not encode destructive cleanup in a routine migration or startup command.
