# Tasks

## 1. Persistence and migration

- [x] 1.1 Add separate model and manual category associations and an explicit override marker; migrate existing assignments, inactive options, provenance and revisions, and verify them on an isolated database with fictional records.
- [x] 1.2 Implement loss-aware downgrade guards and document backup, coordinated deployment and rollback; verify representable and non-representable cases on isolated data.

## 2. Classification and API

- [x] 2.1 Update the decision contract and worker to validate and persist distinct category arrays while preserving manual choices; manually verify empty, multiple, invalid, deactivated, retry and in-flight completion cases with controlled fictional data.
- [x] 2.2 Update category writes and projections with revision checks, manual empty selections and separate model provenance; manually verify stale and concurrent updates, inactive retention, invalid selections and independent priority changes.
- [x] 2.3 Update effective-category filtering without duplicate counts and retain legacy filter parameters; manually verify overlapping category matches, combined filters and populated pagination.
- [x] 2.4 Document the breaking API contract and model output format, including migration examples; compare documentation with actual requests and responses.

## 3. Workspace

- [x] 3.1 Display multiple effective category tags and expose model suggestions and origins; manually inspect empty, inactive, simulated and manual cases at desktop and narrow widths.
- [x] 3.2 Add accessible category multi-selection with save, clear, conflict and inactive-retention behavior; manually verify keyboard use, errors, background refresh and preservation of unsaved response text.
- [x] 3.3 Update workspace usage documentation and verify the described workflow against the interface.

## 4. Integration verification

- [x] 4.1 Walk through migration, classification, review, retry and filtering with fictional tickets across themes and viewport sizes; record outcomes and limitations.
- [x] 4.2 Run appropriate non-test build and strict OpenSpec validation checks and report results; do not create, modify or run tests unless explicitly requested.
