# Proposal

## Why

Lumen does not yet have an executable foundation. A reproducible starting point lets us develop subsequent changes without presenting planned features as implemented.

## What Changes

- Create a minimal FastAPI API and TypeScript, HTML and CSS SPA, with an API availability indicator.
- Establish local configuration, locked dependencies and documented startup and build commands.
- Add CI for dependency installation, frontend type checking and build, without test execution.
- Keep the core domain-agnostic; defer tickets, RAG, model roles and LangGraph to later changes.

## Capabilities

### New Capabilities

- `service-health`: basic API process availability without asserting the health of future dependencies.

### Modified Capabilities

None.

## Impact

Introduces API and frontend source, configuration, automation and documentation. PostgreSQL, workers, models and external integrations are not required to start this foundation. Tests are not created or run unless the user explicitly requests them.
