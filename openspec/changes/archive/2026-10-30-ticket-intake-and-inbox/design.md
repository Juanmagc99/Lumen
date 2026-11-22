# Design

## Context

The existing API only exposes process liveness; the Vite SPA proxies that endpoint. There is no persistence or ticket model. See the proposal and capability specs for scope and observable behavior.

## Goals / Non-Goals

**Goals:** Keep ticket persistence independent of HTTP and future processing, give each asynchronous operation a bounded session and transaction, and make retries safe under concurrency.

**Non-Goals:** Design a queue, backfill strategy, processing status, authentication, production deployment, or real integrations.

## Decisions

1. Use PostgreSQL locally through Compose with a persistent volume and explicit environment configuration. Use SQLAlchemy's async engine and asyncpg, with an AsyncSession per request or concurrent task; close sessions and roll back failed transactions. Alembic owns versioned schema changes and runs explicitly, not implicitly on API startup. SQLite and automatic table creation were considered but do not match the selected database and migration approach. Pin compatible dependencies and verify the async migration setup on Windows.
2. Keep HTTP validation, application service, and database access as distinct responsibilities. The service commits creation before returning; no queue, processing record, or event publisher is added now. Later processing must define its own durable handoff and backfill; a database commit followed by a queue publish alone is not atomic.
3. Use a database-generated or application-generated UUID and a timezone-aware UTC receipt timestamp. Store subject and description as data, not instructions. Use an optional `Idempotency-Key` header with a documented bounded, nonempty format. Preserve its association for the lifetime of the ticket; there is no expiration policy in this change. Compare the validated subject and description exactly, without silently normalizing content beyond rejecting whitespace-only values. A unique database constraint and an atomic transaction protect ticket and key association against concurrent requests; on conflict retrieve the existing result and compare content. Return 201 on creation, 200 for an identical replay, and 409 on a mismatched replay. Do not infer duplicates from matching content without a key.
4. Provide `POST /api/tickets`, `GET /api/tickets`, and `GET /api/tickets/{id}`. Return all entries without pagination, newest first with identifier as a deterministic tie-breaker. Use standard validation responses and actionable, non-sensitive storage errors. The Vite proxy forwards `/api` as well as the existing `/health`; production serving requirements are documented.
5. Build a framework-free SPA inbox and detail view, with accessible navigation, loading, empty, missing and failure states. Render ticket data through safe text APIs, not HTML interpolation. Use Impeccable for frontend direction and review when implementing. No creation, edit, delete, or artificial processing state is shown.

## Risks / Trade-offs

- [Unbounded listing grows with ticket volume] → Document the limitation; add pagination in a later change when needed.
- [Concurrent retries or response loss may duplicate tickets] → Enforce uniqueness and transaction boundaries in PostgreSQL, including concurrent conflict handling.
- [Schema changes or startup order can cause failures] → Run explicit Alembic migrations after PostgreSQL is ready and report connection failures clearly.
- [Untrusted ticket content could execute in the browser] → Render content as text and avoid logging ticket bodies by default.
- [Key association is retained indefinitely] → Document its scope and defer expiry or client scoping until requirements exist.

## Migration Plan

Start PostgreSQL, apply the initial Alembic migration, then start the API and SPA. Existing installations have no persisted ticket schema. To roll back, stop the new application and use the migration downgrade only if ticket data may be discarded; retain or back up the volume when data is needed. Keep `/health` process-only.
