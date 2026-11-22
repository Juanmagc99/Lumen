# Proposal

## Why

Tickets are persisted but have no processing path or classification status. A durable background workflow provides automatic, observable classification without making receipt depend on a running worker or model provider.

## What Changes

- Atomically record each new ticket and a pending classification job in PostgreSQL, and process jobs with a managed worker.
- Store a fixed, explicitly simulated classification, expose processing status in the inbox and detail, and permit manual retry after automatic attempts are exhausted.
- Configure the local database user, password, and database name through `.env`; start and manage the worker with the development tooling.
- As a one-time development operation, clear Lumen's existing local data while retaining database structure, after verifying the target. Do not delete the PostgreSQL volume.
- Defer real LLM integration, retrieval, response generation, and advanced inbox filters.

## Capabilities

### New Capabilities
- `ticket-classification`: Durable background classification, simulated results, failure recovery, and manual retry.

### Modified Capabilities
- `ticket-intake`: Atomically record pending classification for new tickets while preserving intake independence from the worker.
- `ticket-browsing`: Expose classification status and result and provide retry for failed classification.
- `local-development-environment`: Manage the worker and configure database identity through local settings.

## Impact

The API, database schema and migrations, worker lifecycle, development scripts, configuration examples, documentation, and SPA will change. Existing local Lumen data will be cleared once at implementation time, subject to identifying the intended database. No external broker or real model is required.
