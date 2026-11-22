# Proposal

## Why

A ticket can concern more than one topic, but the current classification retains only one category. Allowing multiple categories makes both model suggestions and human review reflect the ticket more accurately.

## What Changes

- Allow the decision model to suggest zero or more active categories and at most one priority, retaining explicit insufficient-evidence behavior.
- Let operators review and replace the complete category selection; a manual selection takes precedence over later model results, which remain separately inspectable.
- Show and filter tickets by their effective categories, retain inactive historical associations, and protect concurrent edits.
- Preserve existing single-category assignments and provenance during migration.
- **BREAKING**: Replace singular category fields in ticket classification API contracts with category collections; update the SPA and document migration for API clients.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ticket-classification`: Produce and retain multiple category suggestions while preserving manual precedence and provenance.
- `ticket-browsing`: Present, edit, and filter multiple effective categories per ticket.

## Impact

Classification persistence and migration, decision-model contract and validation, worker, ticket API, inbox and detail views, and documentation are affected. Existing options and single-priority behavior remain in place. No additional infrastructure is expected.
