# Design

## Context

The current response is one PostgreSQL row per ticket with an optimistic revision and no text history. Classification already uses durable PostgreSQL jobs, expiring claims and a LiteLLM decision adapter. Knowledge ingestion, profiles and response generation do not yet exist. See the proposal for motivation.

## Goals / Non-Goals

**Goals:** Preserve human work and immutable AI originals; make evidence, attempts and resource use inspectable; support multiple worker processes without a new service.

**Non-Goals:** Sending messages, OCR, secure tenant isolation, automatic ticket response generation, and exact attribution of every character in mixed text. PDF and other binary document formats are deferred; this initial slice accepts UTF-8 text and Markdown files and pasted text.

## Decisions

### Knowledge and retrieval

Introduce named knowledge bases, documents, immutable document versions, and stable text chunks. The operator explicitly selects a base or generation without a base; a base is not an authorization boundary. Persist source content and chunks in PostgreSQL. Ingest UTF-8 text and Markdown with bounded upload size and explicit decoding errors; process asynchronously with visible state and bounded recovery. Index ready chunks using PostgreSQL full-text search and rank a bounded set of matching chunks. This is lexical RAG and avoids embedding costs and another service; semantic retrieval can be added behind a retrieval port later. Persist the selected chunk IDs, version IDs and excerpts or immutable references for audit. New retrieval excludes deactivated documents and versions superseded by a ready version; the previous ready version remains active until a replacement is ready.

### Generation and evidence

Create a durable request and attempt records, following the existing claim-token pattern. Separate retrieval and response-model ports from persistence and HTTP. An explicit request snapshots the ticket input and selected knowledge base; record the actual retrieved versions and prompt/configuration version used by each attempt. Treat ticket and document content as untrusted data, limit context, validate structured outputs and citation IDs against retrieved evidence, and display cited excerpts. A citation's existence does not prove its claim; reviewers assess support. If retrieval has no meaningful matches, return an insufficient-evidence result without a model call. If the model reports insufficient evidence, retain that result and avoid portraying it as verified. Reject or clearly flag invalid citations rather than inventing replacements.

Without a base, skip retrieval and use a distinct prompt and configuration identifier. Permit general suggestions based on the ticket, but instruct the model to identify missing specific information, avoid invented organization-specific facts and citations, and distinguish suggestions from established facts. Reject any returned citation. Record the absence of a base and show that no sources were consulted on every resulting suggestion. These instructions do not guarantee factual accuracy; human review remains necessary. Existing base-backed requests never fall back silently to this mode.

### Response and provenance

Keep `ticket_responses.text` as the visible editable text. Store each completed AI original on its immutable generation record, linked to the ticket, and reference the adopted generation from the response. This is logically the requested separate original and visible fields while allowing multiple generations without overwriting prior originals. Adoption is explicit and confirms replacement of nonempty editor text; it does not silently save or approve. An existing revision check protects the eventual save. Track manual, AI-adopted, and AI-edited provenance based on explicit adoption and comparison with the adopted original; do not infer authorship of individual passages. Retain the link when editing or approving. If another suggestion is adopted, link the new source; prior generation records remain. A manual response created without adoption has manual provenance. No prior visible response history is required.

### Limits, recovery and cost

Use PostgreSQL-coordinated slots and timestamped reservations to enforce configurable maximum concurrent response calls and requests per time window across workers. Acquire capacity atomically before every actual provider attempt, including retries. Do not hold a database transaction open during the call. Capacity leases must outlast the configured provider timeout plus cleanup margin and be recoverable after worker failure; an expired claim cannot commit a result. Network timeouts can leave the provider outcome unknown, so retries may incur duplicate charges: record each attempt and do not promise exactly-once billing. Bound queue, request size, attempts, timeouts and retry delays; expose overload and errors. Keep response limits separate from classification unless explicitly configured otherwise. A budget cap and token-per-minute enforcement are future extensions, not implied by a request-rate limit.

Record requested and provider-reported model, provider, timestamps, status, duration, usage, provider request ID if supplied, and estimated cost only with an explicit pricing basis and currency. Use null for unavailable values; credits are provider-specific. Preserve a brief evidence-based rationale as generated explanation, not hidden chain of thought or proof of correctness. Avoid credentials in records and logs; expose sanitized failures. Document retention and access limitations for stored content.

### UI and compatibility

Add a knowledge workspace for bases, content, state, retry and deactivation; add generation state, source inspection, audit and suggestion adoption to ticket detail. Existing response editing, conflict protection and approval remain available when ingestion or generation fails. Continue to use the response role separately from classification. Provide settings and fictional examples without credentials.

## Risks / Trade-offs

- [Lexical retrieval misses paraphrases] → Surface insufficient evidence; use bounded, inspectable chunks and leave a retrieval port for a later semantic approach.
- [Prompt injection or unsupported output] → Isolate untrusted material, validate references, expose evidence and require human review; no prompt alone guarantees correctness.
- [Worker crash or ambiguous timeout causes duplicate cost] → Persist attempts and leases, bound retries and report unknown outcomes.
- [Historical knowledge and model outputs increase storage] → Retain references needed for audit and document operational retention; deletion policy requires separate design.
- [No authentication] → Knowledge-base selection is not tenant isolation; use fictional data in the demo.

## Migration Plan

Add tables and nullable provenance links with Alembic; preserve existing response text, status and revisions and classify preexisting rows as manual. A further migration permits a null base on generation records; downgrade must refuse while such records exist. Deploy schema before API and worker, configure the response role and limits, then enable generation. Rollback application code only while retaining new tables and data; destructive downgrade would discard audit and knowledge history and must be handled separately. Update setup documentation with supported formats, settings and known limits.
