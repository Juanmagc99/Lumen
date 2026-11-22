# Design

## Context

See `proposal.md` for the motivation. FastAPI routes in `main.py` access persistence directly, `tickets.py` combines request/response models and SQL queries, and `worker.py` owns polling, claims, model calls, validation, and completion. PostgreSQL provides the durable queue and concurrency controls; Alembic imports the current database configuration and ORM metadata. `scripts/dev.ps1` launches both processes and migrations. The main OpenSpec capabilities define the behavior that must survive the transition.

## Goals / Non-Goals

**Goals:** Keep dependencies directed toward application and domain code; make entry points thin; make transaction boundaries and worker ownership explicit; preserve observable behavior and existing data throughout reviewable phases.

**Non-Goals:** Changing the API or database schema, replacing PostgreSQL or LiteLLM, adding a response-generation role, introducing a generic plugin system, introducing new infrastructure, or revising product behavior. Simulated historical results remain readable; no simulated fallback is added.

## Decisions

1. **Use one Python package with explicit boundaries.** Under `apps/api/lumen/`, organize `domain/`, `application/`, `adapters/inbound/http/`, `adapters/inbound/worker/`, `adapters/outbound/db/`, `adapters/outbound/llm/`, and `bootstrap/`. The exact module granularity should follow actual responsibilities rather than a file per class. Domain and application must not import FastAPI, SQLAlchemy, LiteLLM, concrete adapters, or process environment. Python protocols and small immutable data structures are sufficient; no dependency injection framework is needed. Explicit construction at process entry points supplies adapters and configuration. This is preferred to merely relocating current modules, which would retain their dependency cycles and shared infrastructure types.

2. **Treat HTTP and the worker as inbound adapters.** HTTP routers own Pydantic request/response contracts, validation, status codes, and translation of application errors; they call use cases instead of issuing SQL. Application-owned inputs, results, and errors cross the boundary, not ORM instances or HTTP exceptions. The worker owns polling, process lifetime, and safe operational logging, and invokes a classification use case. This keeps request handling and scheduling replaceable without duplicating business orchestration.

3. **Use purpose-specific outbound ports.** Application-facing interfaces express ticket intake, queries, option management, job claiming/completion and decision generation using application/domain values. Read projections may be tailored to list and detail queries rather than pretending every query is an aggregate. PostgreSQL adapters own SQLAlchemy models, query construction, mapping, database exceptions and transaction mechanics. A small set of meaningful operations is preferred to a generic repository or a port for every table. The application expresses retry and classification policy while atomic state transitions and invariants requiring locks are enforced by the persistence operation.

4. **Make transactional guarantees part of the ports.** Ticket, idempotency key, and pending job are committed together; a conflicting replay returns the existing ticket only for identical content. Claiming selects eligible work with `SKIP LOCKED`, increments attempts, assigns an expiring token, and commits before inference. Completion locks the job, checks current token and expiry using database time, locks and rechecks active options, checks expiry again after locking, then commits the result or bounded retry/failure atomically. No database transaction remains open during the model call. A stale or expired claim must never finalize. Manual retry updates only a failed job atomically. Preserve maximum attempts, delays, failure reasons, `unavailable` status for missing jobs, and existing historical result/source semantics. Do not promise exactly-once inference: lease expiry can cause repeated provider calls.

5. **Isolate decision inference.** A decision-model port accepts ticket text and a snapshot of active category/priority options and returns a structured decision or a classified failure. The LiteLLM adapter owns provider configuration, the untrusted-data prompt, payload encoding, timeout, response decoding, and provider-specific errors. The application validates returned IDs against the snapshot; the PostgreSQL completion operation revalidates active membership under lock. Missing options, malformed or out-of-snapshot decisions, configuration failures, and provider failures retain their current outcomes. Keep the decision role separately configurable; do not build a speculative response adapter. Never log credentials, raw ticket text, or provider payloads.

6. **Manage resources at process boundaries.** Build database configuration lazily enough that `GET /health` works without database or model credentials. Prefer one asynchronous engine/session factory per process with bounded sessions, rollback on error, and disposal on shutdown; do not share live sessions across requests or model calls. Alembic uses its own appropriate migration engine and imports the relocated metadata. Preserve `DATABASE_URL` precedence and all current environment names. Compare observable startup and failure behavior before changing lifecycle semantics; if safe disposal or process behavior cannot be verified, retain the existing lifecycle and document the limitation rather than introducing a regression.

7. **Preserve compatibility during incremental delivery.** Each phase leaves API, worker, migrations, and development commands runnable. Temporary forwarding modules may bridge imports during the transition but are removed at completion. Preserve HTTP paths, validation, status codes, response shapes, filter semantics, configuration, migration history, persisted data, and no-credential health behavior. Update `scripts/dev.ps1`, Alembic configuration/imports, and documentation when entry points move. No schema migration is expected; if one becomes necessary, stop and revise the change rather than silently expanding scope.

8. **Repair local decision-model configuration.** The existing `.env` loader rejects the documented `LUMEN_DECISION_MODEL`, `LUMEN_DECISION_API_KEY`, and `LUMEN_DECISION_TIMEOUT_SECONDS` settings. Accept these names and supply their values only to the worker process, preserving `.env` precedence over the caller's environment. Disable python-dotenv's implicit loading when the worker imports LiteLLM: manual launches must use explicitly exported settings and must not silently load a parent `.env`. Avoid putting values in arguments, output, or logs. This corrects the existing `local-development-environment` requirement rather than introducing a new capability.

## Risks / Trade-offs

- **Concurrency regressions** -> Keep lock ordering, claim fencing, database-time expiry checks, active-option revalidation, and transactional handoff explicit. Manually exercise concurrent claims and stale completion with isolated fictional data.
- **API or operational drift** -> Compare response contracts and local commands against existing specs, including idempotency, filters, failure statuses, health without credentials, startup, and migrations.
- **Adapter leakage or unnecessary indirection** -> Review imports and boundary types; add interfaces only for real dependencies and use cases.
- **Provider calls may cost money and repeat** -> Prefer controlled manual checks using an explicitly configured provider only when available; report what was not verified. Never send real data or expose credentials.
- **Manual verification has limited coverage** -> Record observations and unverified scenarios; do not create, modify, or run automated tests without an explicit request.

## Migration Plan

1. Establish package and composition without changing external behavior; keep both processes and migrations runnable.
2. Extract classification orchestration, durable job operations, and LiteLLM adapter while preserving claim and completion transactions.
3. Extract ticket and option use cases, HTTP routers, database mappings and query adapters; preserve API responses and filters.
4. Remove temporary bridges, align lifecycle, entry points, migration imports and docs, and perform integrated manual checks using isolated fictional data.

No database schema or data migration is planned. Roll back by restoring the previous code and entry points against the unchanged schema and existing data; do not reset or delete a shared development database. Apply each phase with its corresponding startup/import changes together, and record any check that could not be performed.
