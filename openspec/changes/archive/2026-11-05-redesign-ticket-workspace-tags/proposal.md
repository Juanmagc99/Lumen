# Proposal

## Why

Ticket classification is visually detached from ticket metadata, and the response editor does not stand out as the primary workspace. Operators need recognizable, editable labels in the inbox and detail, with a straightforward way to manage them.

## What Changes

- Present named, colored category and priority tags in the inbox and near the top of ticket detail, on separate category and priority rows in detail, with room for multiple category tags.
- Allow an operator to change the ticket's category and priority; preserve manual choices against asynchronous model results and indicate their origin discreetly.
- Extend the existing classification-options workspace into a tag backoffice with editable colors and existing lifecycle controls.
- Give description and response distinct visual areas while preserving human review, drafts, approval and unsaved text protection.
- Preserve explicit classification progress, failures, retry, undetermined values and historical result provenance.
- Keep the current single category per ticket in this change; support for assigning multiple categories is a subsequent feature, not an implemented capability here.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `classification-options`: Add color management and tag presentation to existing categories and priorities.
- `ticket-browsing`: Present tags and revise detail hierarchy; support manual ticket classification changes while preserving operational states and filters.
- `ticket-classification`: Protect manual selections from automated results and retain distinguishable provenance.
- `ticket-response`: Present the response as a distinct workspace without changing approval semantics.
- `workspace-navigation`: Identify the existing classification-options destination as the tag management backoffice.

## Impact

The SPA, classification option and ticket APIs, worker persistence, database migrations, and documentation are affected. Existing ticket data, filter URLs, historical simulated results, and retained database associations require a compatible migration. No new infrastructure is expected.
