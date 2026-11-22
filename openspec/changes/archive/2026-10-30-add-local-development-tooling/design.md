# Design

## Context

Compose currently runs PostgreSQL; the API runs through uv and the web through npm in separate PowerShell terminals. Database initialization requires a local password and Alembic migration. Vite proxies to the API, and `/health` only indicates API process availability. See proposal.md and the local-development-environment spec for scope and behavior.

## Goals / Non-Goals

**Goals:** Provide a Windows PowerShell development workflow with an extensible command surface and safe background process ownership.

**Non-Goals:** Production orchestration, new container images for the applications, database resets, and support guarantees for other operating systems.

## Decisions

1. Use a root Makefile as a thin interface over Windows PowerShell 5.1 helpers, so the commands work without a separate PowerShell 7 installation. Document a compatible Make installation. PowerShell handles Windows process management and secrets. A Make-only solution couples lifecycle logic to shell-specific recipes; containerizing all services would add unnecessary deployment machinery.
2. Retain Compose for PostgreSQL and existing uv/npm commands for the applications. Start the healthy database, run Alembic, then launch API and Vite. Detect actual startup failure and report addresses; do not treat the API health endpoint as database readiness. Explicit setup installs locked dependencies instead of silently reinstalling on every start.
3. Store local process metadata and separate logs in an ignored runtime directory. Record enough identity, including process creation time and executable or command context, to detect stale or reused PIDs; fail safely when identity cannot be established. Manage the complete launched process tree without killing unrelated processes. Use the shared Compose project identity `lumen` across checkouts so they use the same database and volume; stopping its database affects every checkout using it. A bare PID file or port-based termination is unsafe.
4. Load the local password and optional ports from the ignored root `.env`, using `.example.env` as a credential-free template. Parse configuration as data without executing it; file values override inherited settings. Derive an encoded database URL in memory for migration and the API. Do not write secrets into runtime metadata, logs, tracked files, or command-line arguments. Keep current volume/password initialization semantics and explain how to reuse the password.
5. Make start idempotent and track what each invocation started. On partial failure, clean up only resources started by that invocation, or clearly report remaining resources and recovery steps. Never adopt unrelated listeners. Stop uses Compose without removing volumes; restart stops successfully before starting. Status distinguishes managed application process state, database state, and readiness rather than presenting a single misleading health result.
6. Expose `help`, `setup`, `dev-start`, `dev-stop`, `dev-restart`, `dev-status`, and `dev-logs`; keep service definitions and lifecycle operations structured so future services can be added. Logs should have bounded, understandable output and be accessible after a process exits.

## Risks / Trade-offs

- [Windows process wrappers may spawn children and PID reuse can target a different process] → Track and verify identity, handle the process tree, and refuse unsafe termination.
- [Existing ports or Compose services may belong to other work] → Detect conflicts, use the explicitly shared `lumen` Compose project, and never kill listeners by port. Document that stopping its database affects all checkouts using it.
- [Partial startup or stale state can mislead operators] → Report per-service status, clean up only owned resources, and document recovery.
- [Local logs may contain application data] → Ignore runtime files, avoid secrets, and document local log retention and cleanup.

## Migration Plan

Add the commands alongside existing manual instructions, then document the new primary workflow and recovery. The shared `lumen` Compose project uses its existing named volume if present; volumes belonging to other Compose projects are not migrated or deleted automatically. Rollback removes the new tooling without deleting persisted data.
