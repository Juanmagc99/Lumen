# Design

## Context

Ticket details are loaded by the SPA and automatically refreshed while classification is in progress. Backend operations use application ports and PostgreSQL adapters. The current schema contains no response. See proposal.md for scope and the delta specs for behavior.

## Goals / Non-Goals

**Goals:** Persist one response safely, protect work in the editor, and preserve existing ticket and classification behavior.

**Non-Goals:** AI-generated drafts, documents, profiles, historical versions, identity, external sending, or new infrastructure.

## Decisions

1. Use a separate one-to-one response table keyed by ticket ID, with nonblank text, draft/approved state, UTC last-text-edit timestamp, and an integer revision. A missing row means no response. This leaves existing tickets and listing queries intact; embedding nullable response fields in tickets would couple independent data unnecessarily.
2. Expose response retrieval and explicit save-draft and approve operations through application use cases and HTTP. Both write operations carry the current editor text and expected revision (or an explicit absent precondition for creation). Each is an atomic conditional write; stale revisions and competing creation return conflict. Approval can persist unsaved text atomically. Failed writes leave the existing persisted record intact. Preserve text verbatim, using whitespace-only validation; unchanged text leaves the edit timestamp unchanged. State changes increment the revision even if text does not. A simple last-write-wins approach would silently lose work.
3. Place an accessible editor and status in ticket detail. Keep local editor state separate from classification refresh and guard navigation with unsaved changes; report saving, errors and conflicts while retaining local content. On conflict, present the saved version and a clear recovery path without overwriting local text. Render all response content as text. Avoid a full detail replacement that destroys an active editor.
4. Apply state transitions on successful writes only: absent to draft or approved; draft to draft or approved; approved with changed saved text to draft; unchanged saves preserve approved state. Approval is an explicit operator action. The timestamp measures text changes, not approval or opening the editor.

## Risks / Trade-offs

- [No history] Previous text is lost on a successful edit. This is intentional; the latest timestamp is not an audit trail.
- [Concurrent sessions] Edits can conflict. Revision checks and a recovery UI avoid silent overwrites.
- [Background refresh and navigation] Unsaved text could be lost. Isolate editor state and warn on departure, including browser unload where supported.
- [No identity] The last edit time cannot establish who made it.

## Migration Plan

Add a versioned migration for the response table without modifying existing tickets, deploy API and web together, and document the response endpoints and timestamp semantics. Before downgrade, back up/export any response text: dropping the table would permanently discard it. No existing response needs backfilling.
