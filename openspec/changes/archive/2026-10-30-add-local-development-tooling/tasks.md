# Tasks

## 1. Command interface and setup

- [x] 1.1 Establish the supported Windows Make invocation, add a thin root Makefile and help output, and verify that all documented targets are discoverable.
- [x] 1.2 Implement setup using the locked uv and npm dependencies, document prerequisites and setup in the README, and verify successful and failed prerequisite handling manually.

## 2. Development lifecycle

- [x] 2.1 Implement project-scoped Compose startup, credential handling, database readiness, and migrations; verify missing credentials and migration failures are reported without exposing secrets.
- [x] 2.2 Implement background API and web startup, per-service logs, ignored runtime state, port conflict detection, and process identity tracking; verify repeated startup does not duplicate services or adopt unrelated listeners.
- [x] 2.3 Implement safe stop and restart for managed process trees and the scoped database service; verify stale or reused process identities do not terminate unrelated processes and the database volume is retained.
- [x] 2.4 Implement per-service status and bounded log access, and document commands, secret handling, runtime files, extension points, and recovery; verify the documented commands and stopped-service output manually.

## 3. Integration verification

- [x] 3.1 Manually exercise startup, repeated startup, status, logs, restart, stop, and startup after stop with fictional data; verify data persists and report the checks performed.
- [x] 3.2 Manually exercise occupied ports and partial startup failures in an isolated environment; verify cleanup or recovery guidance and preservation of unrelated processes and data.
