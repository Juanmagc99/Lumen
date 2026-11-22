# Tasks

## 1. Persist options and manual choices

- [x] 1.1 Add migration and persistence for option colors, per-field manual overrides and revision; verify migration on an isolated database with existing fictional classifications and inactive options retained.
- [x] 1.2 Extend option contracts and management for validated colors with backward-compatible defaults; verify create, recolor, invalid input and rename using fictional options, and document the API changes.
- [x] 1.3 Add revision-checked manual classification updates with active/type validation and effective values; manually verify independent field edits, persistence, conflicts and invalid choices.
- [x] 1.4 Update list/detail projections and filtering to use effective values while retaining legacy model fields and provenance; manually verify combined filters, pagination and inactive associations and document API behavior.
- [x] 1.5 Ensure worker completion and retry cannot replace manual choices; manually inspect concurrent edits and a controlled in-flight completion for both fields.

## 2. Ticket workspace and tag administration

- [x] 2.1 Extend the existing options view with accessible color editing and tag previews; manually verify add, edit, cancel, activation and light/dark appearance.
- [x] 2.2 Update navigation and retain existing options links; manually verify navigation and keyboard access on narrow and wide screens.
- [x] 2.3 Redesign inbox rows to display named colored effective tags and relevant processing states; manually verify filters, pagination, refresh, missing values and historical results.
- [x] 2.4 Redesign ticket detail with separate category and priority rows and accessible editing, discreet provenance, states and retry; manually verify successful edits, errors, conflicts and inactive values.
- [x] 2.5 Give description and response distinct visual areas without changing response workflow; manually verify draft protection, approval and background refresh, and update user documentation.

## 3. Integration verification

- [x] 3.1 Inspect the complete flow with fictional tickets across desktop and narrow widths, themes and keyboard navigation, including saved manual tags and model completion; record results and limitations.
- [x] 3.2 Run appropriate non-test build and OpenSpec validation checks and report results; do not create, modify or run tests unless explicitly requested.
