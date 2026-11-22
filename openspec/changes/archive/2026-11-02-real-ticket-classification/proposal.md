# Proposal

## Why

The current worker produces a fixed simulated classification, so it cannot help operators organize incoming tickets. Operators need configurable categories and priorities and real model suggestions that can be used to browse tickets.

## What Changes

- Replace simulated classification of new jobs with a configurable decision model accessed through LiteLLM. Persist at most one category and one priority, allowing each to be undetermined when evidence is insufficient.
- Provide application-managed global category and priority lists, seeded with generic editable defaults. Preserve historical references when options are renamed or deactivated.
- Show results and support category and priority filters in the inbox and detail. Preserve the existing paginated filtering behavior.
- Preserve asynchronous PostgreSQL jobs, safe intake, bounded retries, and manual retry. Handle provider and invalid-output failures without inventing results.
- Provide local server-side credential configuration and clearly identify real versus historical simulated results.
- **BREAKING**: Classification result representation changes to structured category and priority values; API and SPA must be updated together.
- User accounts, authorization, profiles, response generation, LangGraph, and external messaging are outside this change.

## Capabilities

### New Capabilities

- `classification-options`: Manage global category and priority options and their lifecycle.

### Modified Capabilities

- `ticket-classification`: Replace simulated classification with validated real-model decisions while retaining durable processing.
- `ticket-browsing`: Display and filter structured category and priority results.
- `local-development-environment`: Configure the decision model and server-side credentials for the worker.

## Impact

PostgreSQL schema and migration, FastAPI contracts and filtering, worker and configuration, LiteLLM dependency, SPA management and inbox views, and development documentation change. Model calls transmit ticket content and configured options to the selected provider and can incur cost. Existing simulated results need explicit preservation without being mislabeled as real decisions.
