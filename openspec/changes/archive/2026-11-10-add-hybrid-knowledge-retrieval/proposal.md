# Proposal

## Why

Lexical retrieval can miss relevant knowledge expressed in different words, leaving an operator without useful evidence. Combining semantic and lexical retrieval can improve coverage while retaining exact-term matches and reviewable sources.

## What Changes

- Apply hybrid retrieval to every knowledge base, using OpenAI embeddings with an independently configurable model and credential.
- Index existing and new document versions and combine semantic and lexical candidates within the selected base.
- When semantic retrieval is unavailable or incomplete, use lexical retrieval and visibly disclose the degraded mode; preserve insufficient-evidence handling and citations.
- Expose indexing progress and failures, support recovery, and document provider data transfer and usage costs.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `grounded-response-generation`: Retrieve hybrid evidence and disclose lexical-only fallback.
- `knowledge-management`: Track and recover semantic indexing for all knowledge bases and existing documents.

## Impact

The API, worker, PostgreSQL storage and migrations, retrieval and ingestion adapters, configuration, and SPA generation and knowledge views will change. OpenAI receives document fragments and ticket queries to produce embeddings; embedding calls incur usage costs. Existing response review and historical citations remain intact.
