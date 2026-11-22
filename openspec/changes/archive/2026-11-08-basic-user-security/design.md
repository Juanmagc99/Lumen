# Design

## Context

The SPA uses same-origin `/api` requests via Vite or a deployment proxy. FastAPI routers currently expose workspace operations without identity checks, while PostgreSQL and Alembic already provide persistence and migrations. `/health` is intentionally independent of the database. See the proposal and capability specs for scope and behavior.

## Goals / Non-Goals

**Goals:** Enforce current account permissions for direct API calls, keep existing shared data and editing workflows, and provide operable account bootstrap and recovery.

**Non-Goals:** External identity providers, self-registration, email delivery, per-group isolation, and a claim of production deployment readiness.

## Decisions

### Local accounts and opaque sessions

Store unique case-insensitive usernames, Argon2id password hashes via a maintained password-hashing dependency, role and active state in PostgreSQL. Use high-entropy random opaque session tokens in an HttpOnly, SameSite=Strict cookie; store only a cryptographic digest of each token with user ID, creation and absolute expiry timestamps. Use a fixed 12-hour session lifetime and revoke sessions on sign-out, password reset or deactivation. Each protected request loads current account status and role; role changes therefore take effect immediately. Stateless JWTs were considered but complicate immediate revocation and role changes.

Require HTTPS with Secure cookies outside explicitly configured local development; fail closed for unsafe external configuration. Configure a canonical public origin and validate Origin on all state-changing requests, including login and logout; allow a same-origin Referer fallback when Origin is absent and reject requests without either. Require JSON for authentication and account mutations. Do not trust forwarded headers from unconfigured proxies. This protects cookie-based operations from cross-site requests; no session secret belongs in localStorage.

### Account operations and recovery

Administrators create accounts with initial passwords supplied through the UI, change roles, deactivate/reactivate users and reset passwords. Enforce a minimum 12-character password and do not log or return credentials. Users can change their own password after supplying the current one; changing it revokes all their sessions. Do not expose self-registration or account enumeration via login errors. A database transaction and lock protect the last active administrator invariant under concurrent changes.

An explicit local CLI command reads the first administrator's username and password interactively without echo. The local development launcher can alternatively read optional administrator credentials from its ignored `.env` and bootstrap after migrations. Both paths succeed only when the users table is empty, under a transaction preventing concurrent bootstraps. The environment bootstrap permits a short demo password; normal account creation and changes retain the 12-character minimum. A separate local recovery command resets an existing administrator password through the same private prompt and revokes sessions; it requires trusted host and database access. Credentials never appear in command arguments, logs, example files or committed data.

### Authorization boundary

Centralize authentication and authorization dependencies at the HTTP boundary, with explicit role policy for every route and deny by default for new API endpoints. Both roles can operate tickets, generate and approve responses and read or manage knowledge. Both can read classification options; only administrators can modify them or manage accounts. `/health` remains public, as do narrowly scoped login endpoints; session inspection and logout require a valid session. Keep workers independent of browser sessions and do not expose worker internals over HTTP. This preserves application use-case boundaries and keeps policy enforcement server-side rather than relying on hidden controls.

### Failed sign-in throttling

Persist bounded counters for username and client address in PostgreSQL, apply a temporary 15-minute cooldown after five failures in 15 minutes, and return generic failures for nonexistent, inactive and incorrect credentials. Use a dummy password hash for nonexistent accounts and atomically update counters across API processes; clean up expired records. The deployment must provide a trustworthy client address or use the direct peer address, never arbitrary forwarded headers. Per-process memory counters were considered but would reset on restart and diverge between processes.

### SPA interaction

Load session state before opening protected views; display identity, role and sign-out, plus account administration for administrators. Hide restricted option editing from operators while retaining read access. Handle 401 centrally and present reauthentication without discarding an open response editor; after sign-in, require an explicit retry of unsaved work. Surface 403 and service failures distinctly. Maintain keyboard access and responsive layouts consistent with the existing SPA.

## Risks / Trade-offs

- [Cookie configuration or proxy mistakes expose sessions] -> Default to secure cookies, exact origin validation, explicit trusted proxy settings and documented HTTPS deployment assumptions.
- [Account lockout can impede recovery] -> Provide a local, access-controlled administrator password recovery command and transactional last-admin protection.
- [Throttling by client address can affect shared networks] -> Combine account and address limits, bound cooldowns and document operational behavior.
- [Existing integrations lose anonymous access] -> Document the breaking API change and preserve only health and login as public endpoints.
- [Security controls are unverified without explicit test authorization] -> Record checks actually performed and do not claim comprehensive security assurance.

## Migration Plan

Apply additive user, session and throttling migrations without changing existing ticket and knowledge records. Configure origin and cookie security, bootstrap the first administrator locally or through the local launcher environment, then start the upgraded API and SPA. Existing data remains shared. Roll back application code only in a trusted local environment: older versions expose the API without authorization; retain additive tables unless a separate reviewed migration removes them.
