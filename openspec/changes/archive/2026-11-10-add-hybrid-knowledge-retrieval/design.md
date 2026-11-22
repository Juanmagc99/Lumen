# Design

## Context

The current worker splits document versions into immutable chunks and uses PostgreSQL full-text search through a retrieval port. Ingestion readiness and source version identity already exist. The generation workflow records evidence and returns insufficient evidence when none is retrieved. See the proposal and delta specifications for the desired behavior.

## Goals / Non-Goals

**Goals:** Retain lexical availability while indexing asynchronously; make degraded retrieval and index coverage observable; preserve selected-base isolation, evidence provenance and human review.

**Non-Goals:** Automatic external messaging, replacing the response model, per-base enablement, and claiming that semantic similarity verifies a response.

## Decisions

1. Add an embedding provider port and an OpenAI adapter with independently configurable model, dimensions, credential and timeout. An existing OpenAI credential may be configured for this role; never log it. Use bounded batches, timeouts and retries. Keep decision and response roles unchanged. Provider calls send document fragments during indexing and ticket query text during retrieval; document this and associated usage costs. A dedicated port avoids coupling the domain to one provider.
2. Store vectors alongside immutable chunk identity and embedding configuration, using PostgreSQL with pgvector for similarity search. This adds an extension rather than a separate service; document installation and deployment prerequisites. Record model and dimensions so incompatible vectors are never compared. Keep lexical search independent of vector availability.
3. Track semantic indexing separately from ingestion with durable bounded jobs, claim leases, retry and visible status. Schedule active ready versions on deployment and as content becomes ready, idempotently. Reconcile pending work on configuration changes; obsolete work cannot publish vectors for an incompatible configuration. Keep the previous ready document version active until its replacement is ready, as today. Semantic failure does not invalidate lexical readiness or historical citations.
4. Scope both retrieval branches to the selected base, active documents and latest ready versions. When coverage is complete and a query embedding is available, retrieve bounded ranked candidates from each branch, combine by reciprocal rank fusion, deduplicate by chunk ID and apply a bounded context limit. Relevance filtering must avoid treating nearest neighbors as automatically sufficient. Preserve source IDs and excerpts for validation and auditing. A pure vector search would lose useful exact matches; raw scores from different ranking methods are not directly comparable.
5. If the provider, vector search or compatible index coverage is unavailable, use lexical-only retrieval for the entire request and persist the mode and reason with the attempt and outcome, including insufficient-evidence outcomes. Display this warning in generation history and the current result. Do not silently substitute ungrounded generation. An explicit whole-request fallback avoids presenting partial semantic coverage as complete.
6. Expose indexing state and retry in the knowledge view without conflating it with ingestion. Avoid exposing credentials or raw provider errors. Limit concurrency and batch size to manage rate limits, costs and recovery; retain reported embedding usage where available and represent unknown values honestly.

## Risks / Trade-offs

- [Semantic similarity can return irrelevant evidence] → Bound and filter candidates, retain citations and explicit insufficient-evidence handling, and require human review.
- [Reindexing is slow or expensive] → Process durable bounded batches, expose progress, allow lexical fallback, and document expected provider usage.
- [Index coverage changes during retrieval] → Determine coverage and candidates against a consistent active-version/configuration snapshot; otherwise fall back visibly.
- [Extension unavailable or model changes] → Surface degraded status, preserve lexical retrieval, and reindex incompatible vectors rather than mixing them.
- [External provider receives content] → Document the data flow and use fictional data only.

## Migration Plan

Provision the PostgreSQL vector extension, deploy additive schema and compatible API/worker, configure the embedding role, and enqueue existing active ready versions. During backfill, use lexical-only retrieval with a visible warning. Monitor and retry indexing failures. Roll back application code to lexical retrieval if needed; preserve documents, prior citations and response records, and retain or remove vector data only through an explicit migration after backup. Document the downgrade and extension requirements.
