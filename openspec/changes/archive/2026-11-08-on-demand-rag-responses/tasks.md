# Tasks

## 1. Knowledge storage and ingestion

- [x] 1.1 Add migrations and persistence for knowledge bases, immutable document versions, chunks and ingestion jobs; verify existing ticket and response data survives upgrade.
- [x] 1.2 Implement bounded UTF-8 text and Markdown upload, pasted text, versioning, deactivation and ingestion status/retry APIs; verify supported and rejected inputs and historical versions through observable API behavior.
- [x] 1.3 Implement recoverable background chunking and PostgreSQL full-text indexing; verify failed processing remains visible and only ready active versions are retrievable.
- [x] 1.4 Build knowledge management UI and document supported formats, limits and ingestion setup; verify an operator can add, update, inspect and deactivate fictional content.

## 2. Retrieval and generation

- [x] 2.1 Add scoped retrieval and evidence references with stable version and chunk identity; verify selected-base isolation and historical citation inspection using fictional documents.
- [x] 2.2 Add response model configuration and a validated provider adapter separate from classification; verify missing credentials and provider failures are surfaced without fabricated results.
- [x] 2.3 Add durable generation requests and attempts with claim recovery, bounded retries, per-ticket deduplication and explicit insufficient-evidence results; verify states and recovery through API and worker behavior.
- [x] 2.4 Implement database-coordinated concurrency slots and request-window reservations across workers, including retries and lease recovery; verify queued requests wait at configured limits and expired claims cannot commit.
- [x] 2.5 Persist immutable original outputs, inputs, sources, configuration identifiers, attempt diagnostics, usage and estimable costs; verify unknown values remain unknown and credentials are absent.
- [x] 2.6 Validate output citations against retrieved evidence and expose source excerpts and concise rationale; verify unknown citations and untrusted content cannot authorize application actions.
- [x] 2.7 Document response model settings, rate controls, audit fields, pricing assumptions and duplicate-cost limitations; verify documented configuration matches the application.

## 3. Human response workflow

- [x] 3.1 Extend response persistence and API with adopted generation provenance while preserving existing text, status and revisions; verify manual, AI-adopted and edited origins and immutable original output.
- [x] 3.2 Add explicit generation, job progress, suggestion review, evidence and audit views to ticket detail; verify completion does not replace unsaved editor content.
- [x] 3.3 Add explicit adoption with replacement confirmation and preserve optimistic conflict handling, saving and approval; verify edited and concurrent responses remain recoverable and approval sends no external message.
- [x] 3.4 Update product and architecture documentation for the implemented workflow, provenance and limitations; verify it matches observable behavior.

## 4. Integration verification

- [x] 4.1 Manually exercise upload or pasted fictional knowledge through retrieval, generation, editing, approval and source inspection; record results and any unavailable provider-dependent checks.
- [x] 4.2 Manually inspect failure, limit, worker recovery and concurrent-edit paths and report what was and was not checked; do not create, modify or run tests without explicit user authorization.

## 5. Generation without a knowledge base

- [x] 5.1 Persist and process requests without a base, with a separate prompt, audit identifier and citation validation, preserving the existing grounded behavior.
- [x] 5.2 Offer the explicit choice in ticket detail, label source-free suggestions, and document limitations and migration behavior.
- [x] 5.3 Check the migration, application and UI behavior without creating or running tests; report provider-dependent limitations.
