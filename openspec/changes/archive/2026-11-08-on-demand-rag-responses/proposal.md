# Proposal

## Why

Operators can currently write and approve responses manually, but cannot ground an AI suggestion in documentation managed in Lumen. On-demand generation should help them draft while preserving human control, source evidence, and an auditable record of model use.

## What Changes

- Allow operators to add knowledge as uploaded documents or directly entered text, inspect processing status, and select a knowledge base for a ticket generation.
- On explicit request, generate using either scoped evidence from a selected base or ticket information and general guidance without a base. Surface the mode, citations and limitations.
- Process requests through durable jobs with visible state, bounded retries, shared concurrency and rate controls, and per-ticket deduplication.
- Keep suggestions separate from the editable response until explicitly adopted. Preserve each original AI output independently of the visible response text and track its provenance through edits and approval.
- Record generation attempts, source versions, model details, usage, available cost information, and a concise evidence-based explanation for audit.
- Retain human review and approval without sending external messages.

## Capabilities

### New Capabilities

- `knowledge-management`: Knowledge bases, document and text ingestion, versions, and processing status.
- `grounded-response-generation`: On-demand retrieval, generation jobs, evidence, limits, and audit records.

### Modified Capabilities

- `ticket-response`: Adopt AI suggestions without losing manual work, preserve original AI text, and expose response provenance.

## Impact

The SPA gains knowledge management and generation review controls. The FastAPI application, worker, PostgreSQL schema, model configuration, and documentation require extensions; document extraction and retrieval may introduce justified dependencies. Existing manual responses and classification continue to work, and no external ticket message is sent.
