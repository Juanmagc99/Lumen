# Design

## Context

The repository contains initial documentation and OpenSpec configuration. The frontend must be a SPA without UI frameworks and the backend must use FastAPI. See the proposal for scope.

## Goals / Non-Goals

**Goals:** establish a reproducible local development path and CI checks that do not run tests.

**Non-Goals:** implement tickets, persistence, AI, domain profiles or a production environment. Creating or running tests requires explicit user instruction.

## Decisions

1. Use `apps/api` and `apps/web` in one repository. A single package was considered; separate applications keep their contracts and tools independent.
2. Use FastAPI and Pydantic for the API, and Vite with TypeScript, HTML and CSS for the SPA. The initial screen identifies the project and displays the API status or a comprehensible unavailable state. Static files without a build were considered; Vite supports development and type checking without imposing a UI framework.
3. Use a Python virtual environment and reproducible lockfile, plus an npm lockfile. Select a Python version compatible with actual dependencies and use it in CI; the installed local version does not establish compatibility. Document Windows commands and version requirements.
4. Use a development proxy for `/health`, avoiding hard-coded hosts or credentials in the frontend. The endpoint reports API liveness, not readiness of future dependencies.
5. Add CI for dependency installation, frontend type checking and build. Do not add test execution or create tests unless explicitly requested. Starting the foundation does not require credentials or external services. Compose and PostgreSQL are deferred until a change needs them.

## Risks / Trade-offs

- [The foundation does not yet demonstrate the ticket journey] → The next change will introduce the simulated inbox.
- [The installed Python version may not support all future dependencies] → Select and lock a compatible version during implementation.
- [A health indicator can be mistaken for a complete dependency check] → Label and document it as API status only.
- [No automated tests are included at this stage] → Report the checks actually performed and add tests only when the user requests them.

## Migration Plan

No users or persisted data exist. Reverting this change does not require data migration.
