# Tasks

## 1. Identity persistence and local administration

- [x] 1.1 Add the password hashing dependency and additive migrations for users, sessions and bounded sign-in counters; verify migration and model definitions preserve existing workspace tables.
- [x] 1.2 Implement account persistence, Argon2id hashing, unique usernames, password validation and transactional last-active-administrator protection; verify the relevant constraints and transaction paths by code review.
- [x] 1.3 Implement interactive first-administrator bootstrap and local password recovery with session revocation; document both procedures and verify help and credential input do not place secrets in arguments or output.
- [x] 1.4 Bootstrap the initial local administrator from optional ignored environment settings after migrations; verify creation on an account-free database and preservation on subsequent startup.

## 2. Authentication and authorization

- [x] 2.1 Implement opaque session issuance, digest storage, expiration, revocation, current account lookup and persistent sign-in throttling; verify configuration and failure paths by code inspection.
- [x] 2.2 Implement sign-in, session inspection, sign-out, password change and administrator account management endpoints with generic login failures; verify each endpoint's intended access and response contract by route inspection.
- [x] 2.3 Enforce origin validation and secure cookie configuration with explicit local-development settings and trusted proxy behavior; document deployment settings and verify unsafe configurations fail closed by inspection.
- [x] 2.4 Apply deny-by-default authentication and role checks to all API routes while preserving public database-independent health; verify the complete route-to-role matrix against the specifications.

## 3. Workspace integration

- [x] 3.1 Add sign-in, signed-in identity, role display, sign-out and own-password change flows; verify the SPA builds and the controls are accessible at narrow and wide widths.
- [x] 3.2 Add administrator account management and role-aware classification controls; verify operators retain ticket and knowledge workflows and cannot access administrator actions in the UI.
- [x] 3.3 Handle 401, 403 and service failures across protected requests, retaining unsaved response text through reauthentication and requiring an explicit retry; verify the editor and failure paths by inspection.
- [x] 3.4 Update product, architecture and local setup documentation with shared-data permissions, bootstrap, recovery, HTTPS, proxy and rollback limitations; verify instructions match the implemented commands and configuration.

## 4. Integration review

- [x] 4.1 Review the completed implementation against both security specifications, existing data preservation and the route permission matrix; run appropriate non-test build and validation checks and report their results and remaining limitations.
