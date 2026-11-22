# Tasks

## 1. Database and local setup

- [x] 1.1 Add locked compatible SQLAlchemy, asyncpg, and Alembic dependencies and configure PostgreSQL in Compose with a persistent volume; document configuration and verify a clean local installation and database startup.
- [x] 1.2 Configure asynchronous sessions and an explicit initial Alembic migration for tickets and idempotency; document migration commands and verify upgrade against a fresh local database on Windows.

## 2. Ticket API

- [x] 2.1 Implement ticket validation, service, persistence, and creation endpoint; document request and response examples and manually inspect valid, invalid, unavailable-database, and restart-persistence behavior using fictional data.
- [x] 2.2 Implement optional idempotency with atomic uniqueness and conflict handling; document key format and retention and manually inspect replay, conflicting content, unkeyed requests, and concurrent requests.
- [x] 2.3 Implement read-only list and detail endpoints with deterministic ordering and missing-ticket handling; manually inspect populated, empty, and missing responses and document the unbounded-list limitation.

## 3. Inbox and detail

- [x] 3.1 Use Impeccable to shape the framework-free inbox and detail; implement accessible navigation and safe text rendering, and inspect list, detail, mobile layout, and markup-like fictional content in a browser.
- [x] 3.2 Implement loading, empty, missing, error and retry states and update the Vite proxy; inspect these states in a browser with the API available and unavailable.
- [x] 3.3 Update local and production-serving documentation and run the documented frontend typecheck and build; record the results without creating or running tests.

## 4. Integration

- [x] 4.1 Follow the documented setup with PostgreSQL, migrations, API, and SPA; submit a fictional ticket through the API and inspect it in the inbox and detail after restarting the API.
- [x] 4.2 Confirm `/health` still describes only API process availability and review the change against both capability specs; report actual checks and limitations without adding test-running CI.
