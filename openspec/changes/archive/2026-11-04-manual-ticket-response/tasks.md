# Tasks

## 1. Persistence and application behavior

- [x] 1.1 Add the one-to-one response schema and migration with state, timestamp and revision constraints; apply it to an isolated database with fictional data and confirm existing tickets remain unchanged. Document backup and downgrade implications.
- [x] 1.2 Implement response values, application ports, use cases and PostgreSQL operations for retrieval, conditional save and approval; manually check blank input, absent and existing responses, text preservation, status transitions, timestamps, concurrent creation and stale revision conflicts.
- [x] 1.3 Add HTTP operations with validation, not-found, conflict and storage failure mapping; manually inspect responses for creation, retrieval, edits, approval, invalid text, missing tickets and stale writes. Document endpoint contracts and timestamp semantics.

## 2. Ticket detail workflow

- [x] 2.1 Add an accessible response editor, saved status and last edit time in ticket detail; manually inspect absent, draft and approved states and save, edit and approval at desktop and mobile widths.
- [x] 2.2 Preserve unsaved editor content during classification refresh, errors and conflicts, and warn before navigation; manually exercise those paths and verify conflict recovery without silent overwrite.
- [x] 2.3 Inspect safe rendering of markup-like fictional response text and keyboard interaction; update user-facing documentation to explain manual approval and that no message is sent.

## 3. Integrated verification

- [x] 3.1 With isolated fictional data, manually walk through save, reopen, approve, edit, reapprove and restart persistence; check classification and inbox navigation still work, and record limitations.
- [x] 3.2 Run frontend typecheck and production build and strict OpenSpec validation; report results and confirm no tests were created, modified or run.
