# Proposal

## Why

Lumen currently exposes its application API without identifying users or enforcing permissions. Individual accounts and role-based access would allow a team to control who can use the workspace and administer its configuration.

## What Changes

- Introduce individual user accounts, sign-in and sign-out, and administrative account lifecycle management.
- Introduce administrator and operator roles, with authorization enforced by the API for protected operations and reflected in the workspace.
- **BREAKING**: Require authentication for application operations that are currently accessible anonymously; preserve an unauthenticated process health endpoint.
- Provide local interactive and environment-based ways to establish the first administrator without committed credentials. Account recovery and session lifecycle must be addressed in the design.
- Preserve human review and approval of responses; approval continues to save text without sending a message.
- Use one shared workspace: authorized users share tickets and knowledge; tenant or group isolation is outside this change.
- Let operators manage knowledge and review and approve responses, preserving the existing operator workflows; reserve user and classification-option administration for administrators.

## Capabilities

### New Capabilities

- `user-authentication`: Individual accounts, authentication, sessions, and account lifecycle.
- `role-based-access`: Administrator and operator roles and server-enforced access to application operations.

### Modified Capabilities

None proposed: existing workflows retain their behavior for authorized users; access restrictions are owned by the new role-based-access capability.

## Impact

- FastAPI routes and application composition need authentication and authorization boundaries; the SPA needs sign-in and role-aware navigation and feedback.
- PostgreSQL persistence and migrations will be needed for user accounts and possibly sessions; existing tickets, documents, and response provenance must remain available.
- Local setup and product documentation must describe bootstrap, operational assumptions, and the revised security scope. Authentication alone does not establish secure multitenancy or production deployment readiness.
- Credential handling, session protections, recovery, role assignment, and any additional dependencies require design decisions. No test creation or execution is included without explicit user instruction.
