# Tasks

Use the existing main OpenSpec capabilities as the behavioral contract. Perform manual checks with isolated fictional data and record observations and unverified scenarios. Do not create, modify, or run automated tests.

## 1. Package and composition

- [x] 1.1 Introduce the `lumen` package and explicit composition boundaries, keeping temporary forwarding entry points if useful; inspect the resulting imports and confirm API and worker entry points still load.
- [x] 1.2 Align configuration and process startup with the package, preserving environment names and `DATABASE_URL` precedence; manually inspect startup and verify `GET /health` works without database or model credentials.
- [x] 1.3 Align Alembic metadata/configuration imports and development commands with any moved modules; inspect migration discovery and manually verify the local command interface without changing or resetting existing data.
- [x] 1.4 Document the new package and startup conventions as they are introduced; check documented entry points against the actual commands.

## 2. Classification and worker

- [x] 2.1 Define application-owned classification inputs, outputs, errors and purpose-specific ports; inspect imports and confirm they do not depend on FastAPI, SQLAlchemy, LiteLLM, concrete adapters, or process environment.
- [x] 2.2 Extract the LiteLLM decision adapter and structured output handling; manually inspect prompt, untrusted content treatment, payload minimization, timeout, option-snapshot validation and safe error/log behavior.
- [x] 2.3 Extract PostgreSQL job and option-snapshot operations with bounded sessions; inspect transaction boundaries, lock ordering, database-time expiry, token fencing, active-option revalidation and commit-before-inference behavior.
- [x] 2.4 Move classification orchestration and retry policy into application use cases, leaving the worker responsible for polling and lifecycle; manually inspect the mapping of configuration, provider, invalid-decision and no-option failures to the existing bounded retry policy.
- [x] 2.5 With isolated fictional data, manually check pending work, worker restart and expired claim recovery, concurrent claims, rejection of stale completion, deactivated-option revalidation, bounded failures, and manual retry; report any scenario not reproduced and avoid provider calls unless configured and appropriate.
- [x] 2.6 Update worker configuration and architecture documentation for the extracted responsibilities; accept the documented decision-model settings in local `.env` and pass them only to the worker, then inspect configuration precedence and launch behavior without printing credentials.

## 3. Ticket and option operations

- [x] 3.1 Extract ticket creation and idempotency use cases and PostgreSQL operations; manually check atomic ticket/job creation, same-content replay, conflicting replay and concurrent use of a key with isolated fictional data.
- [x] 3.2 Extract ticket list/detail queries and transport mapping; manually check existing response shapes, statuses, UTC date boundaries, literal wildcard search, combined category/priority filters, deterministic ordering and pagination.
- [x] 3.3 Extract classification-option management into use cases and PostgreSQL operations; manually check validation, normalized uniqueness, rename, activation, deactivation and historical associations.
- [x] 3.4 Replace direct SQL and ORM access in HTTP routes with use cases and application-owned results; inspect routes for unchanged validation, response models and error-to-status mapping, including storage failures and retry conflicts.
- [x] 3.5 Update the API and architecture documentation for any moved entry points or internal responsibilities; compare documented contracts and examples with the unchanged external API.

## 4. Integrated cleanup and verification

- [x] 4.1 Remove temporary bridges and unused code, review imports and boundary types, and confirm domain/application contain no framework, adapter or environment imports.
- [x] 4.2 Review engine/session lifetime, rollback and shutdown behavior and keep the existing lifecycle if safe behavior cannot be verified; manually inspect API, worker and migration startup and shutdown without exposing credentials.
- [x] 4.3 Verify an end-to-end flow with isolated fictional data: create or replay a ticket, inspect its pending/completed/failed state as available, browse with filters, and retry a failed classification; record outcomes and provider-dependent limitations.
- [x] 4.4 Check local development start, repeat start, stop, restart, status and migration compatibility without deleting shared data; verify updated docs and record any unavailable environment-dependent checks.
- [x] 4.5 Validate the OpenSpec change and record all manual checks performed, skipped scenarios and remaining limitations; confirm no automated tests were created, modified, or run.
