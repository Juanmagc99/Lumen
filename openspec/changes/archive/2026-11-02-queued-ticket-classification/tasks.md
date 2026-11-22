# Tasks

## 1. Local configuration and data preparation

- [x] 1.1 Configure database user, password, and database name consistently across `.env`, Compose, API, worker, and migrations; document initialized-volume behavior and verify startup configuration without exposing credentials.
- [x] 1.2 Identify the intended local Lumen database and shared usage, stop managed writers, clear only Lumen data while preserving schema and volume, and verify the target tables are empty; stop if the target is uncertain.
- [x] 1.3 Centralize backend configuration for database settings and worker timing in a shared typed module, including the PostgreSQL host port; preserve environment precedence and validate defaults and invalid values manually without exposing credentials.
- [x] 1.4 Connect the API database layer, migrations, and worker to the shared configuration and update setup documentation; manually verify managed startup, liveness without database settings, and database and worker configuration compatibility.

## 2. Durable classification

- [x] 2.1 Add versioned job and result schema with uniqueness and claim constraints; apply the migration and inspect its upgrade and rollback behavior without discarding retained data.
- [x] 2.2 Atomically create pending work with each ticket and preserve idempotent replay; manually inspect persistence, failure behavior, and repeated requests.
- [x] 2.3 Implement a separately runnable worker, fixed simulated classifier, bounded retry and delay, expired-claim recovery, fencing, and atomic result completion; manually inspect success, worker interruption, failure, and concurrent claims.
- [x] 2.4 Expose status, result, and atomic manual retry through the API; manually inspect pending, completed, failed, and duplicate retry responses.

## 3. Development lifecycle and interface

- [x] 3.1 Manage worker start, stop, restart, status, and logs using the existing process safety rules; document commands and manually inspect repeated starts and stopping.
- [x] 3.2 Display classification status in the inbox and detail, show the labelled simulated result, and offer safe retry on failure; inspect desktop and mobile views and loading and failure states.

## 4. Integrated verification

- [x] 4.1 Manually verify ticket creation with the worker stopped, later processing, retries, recovery, and result visibility; report the checks and limitations without creating or running tests.
- [x] 4.2 Run appropriate non-test frontend type and build checks, validate OpenSpec, and document completed checks and any limitations.
