# Tasks

## 1. Embedding storage and configuration

- [x] 1.1 Add the pgvector deployment prerequisite and additive vector, indexing-job and retrieval-audit migrations; document upgrade and rollback, and inspect migration behavior with existing fictional data.
- [x] 1.2 Add independently configurable OpenAI embedding provider settings and adapter with bounded calls, retries and safe errors; document credentials, model, data transfer, usage and costs, and manually inspect missing configuration and provider failure behavior.

## 2. Indexing lifecycle

- [x] 2.1 Add durable, leased, idempotent indexing jobs and active-version backfill with model/dimension compatibility and safe retries; manually inspect recovery, updates, deactivation and configuration changes using fictional documents.
- [x] 2.2 Expose indexing status and retry through the API and knowledge workspace; document the contract and manually inspect pending, ready, failed and retried states while lexical ingestion remains available.

## 3. Hybrid retrieval and review

- [x] 3.1 Implement scoped lexical and semantic candidate retrieval, rank fusion, deduplication and bounded relevance filtering; manually inspect paraphrases, exact identifiers, unrelated content, base isolation and version selection using fictional documents.
- [x] 3.2 Implement lexical-only fallback for unavailable or incomplete semantic retrieval and persist mode and reason with attempts and outcomes; manually inspect provider failure, incomplete coverage and no-evidence cases.
- [x] 3.3 Show retrieval mode and degradation in current results and generation history; document the behavior and manually inspect warnings, citations, insufficient evidence and human approval without external sending.

## 4. Integration

- [x] 4.1 Manually exercise existing-document backfill, new ingestion, hybrid retrieval, provider outage and recovery end to end with fictional data; record outcomes and any unavailable provider-dependent checks.
