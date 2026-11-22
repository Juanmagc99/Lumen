# Proposal

## Why

Operators can inspect and classify tickets but cannot record the response they intend to give. A manual response workflow establishes human review and persistence before AI drafting and knowledge retrieval are introduced.

## What Changes

- Add one manually written response per ticket, with durable draft and approved states.
- Allow saving and resuming a draft, approving its current text, and editing an approved response; saving changed text returns it to draft for renewed approval.
- Display the most recent text-edit timestamp without retaining a version history. Approval saves the text and never sends an external message.
- Add the workflow to ticket detail while preserving classification and navigation behavior.
- Defer profiles, AI drafting, retrieval, citations, response history, and external messaging.

## Capabilities

### New Capabilities

- `ticket-response`: Manual response persistence, editing, review and approval for a ticket.

### Modified Capabilities

- `ticket-browsing`: Permit response editing and approval from the ticket detail while keeping ticket fields read-only.

## Impact

Adds a PostgreSQL migration, response use cases and persistence, HTTP operations, and a detail editor in the existing SPA. Existing tickets remain valid with no response. No model provider or additional infrastructure is required.
