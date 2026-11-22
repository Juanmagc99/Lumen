# Design

## Context

The worker in `apps/api/worker.py` claims PostgreSQL jobs with expiry and fencing, calls a fixed simulator, and stores one text result. Ticket creation and pending work are atomic. The implemented but unarchived `filter-and-paginate-tickets` change adds filtered pagination; this change must integrate with it rather than revert it. See the proposal and capability deltas for scope.

## Goals / Non-Goals

**Goals:** Add provider-backed decisions, manageable options, safe result persistence, and filtering while retaining durable asynchronous intake.

**Non-Goals:** User authentication, authorization, multi-profile configuration, ticket auto-assignment, response drafting, external messages, or orchestration with LangGraph.

## Decisions

1. Use LiteLLM's Python library in the existing worker with a separately configured decision-model identifier and provider credentials. Start with an OpenAI-compatible model selected by configuration; do not hardcode an unverified account-specific model. Structured output is preferred when supported, with server-side schema and membership validation regardless. A direct provider SDK was rejected in favor of the requested provider abstraction; a gateway or LangGraph adds no necessary responsibility to this single-step flow. No fallback to simulation on real-call errors.
2. Store global categories and priorities as distinct option types with stable IDs, editable names, active flags, and database-enforced normalized uniqueness. Seed Inquiry, Incident, Request, Other and Low, Normal, High, Urgent once in a migration. Expose management through the SPA and API without login in the local environment. Deactivation, not destructive deletion, preserves links and filters; renames display current names. Do not reseed at startup.
3. Send only ticket subject, description, and the current active options needed for classification. Treat all ticket and option text as untrusted input; give the model no tools and validate returned IDs and structure. Either dimension may explicitly be undetermined, represented separately from provider failure. Empty option lists fail visibly rather than producing a fabricated decision. Avoid logging raw ticket text, provider payloads, or credentials. Document that content is sent to the configured provider and calls can incur charges.
4. Use snapshots of allowed option IDs for each request and check active membership again atomically before committing; a rename or deactivation during inference must not commit an inactive choice. A changed selection is treated as a recoverable invalid decision. Store option references and source metadata with the job, alongside a way to distinguish undetermined from missing or historical results. Keep old simulated data explicitly labelled and do not silently reclassify existing tickets. New tickets use real inference. Existing failed jobs use the new classifier when retried.
5. Preserve existing claim token fencing and bounded retries. Configure timeouts to fit the claim lifetime or renew the lease safely; provider calls outside database transactions may be repeated after expiry and incur duplicate cost. Classify retryable provider failures, invalid decisions and configuration errors clearly without leaking secrets; retries remain bounded, and retry after correction is available. Do not claim exactly-once model calls.
6. Extend the existing paginated API with category and priority IDs and update UI and API together. Include inactive options in filter choices when historically relevant. Preserve list state and combine new predicates before count and pagination. Existing simulated values remain distinguishable, never coerced into new categories.
7. Keep credential configuration in ignored local environment and load only in the backend worker. Provide credential-free examples and actionable configuration errors; do not add the exposed conversation key to any artifact. The API must accept tickets when the provider is unavailable.

## Risks / Trade-offs

- [Wrong but schema-valid classification] -> Show decisions as model suggestions; retain explicit undetermined and permit option management. Format validation does not prove correctness.
- [Option changes during inference] -> Revalidate IDs against active rows at commit, respecting claim fencing.
- [Provider latency, outages, or cost] -> Bounded timeouts and retries, observable failures, configurable model, and documentation; lease recovery can still duplicate calls.
- [Management has no access control] -> Limit this change to the current local environment; authentication and admin restrictions require a later change before broader exposure.
- [Prompt injection or sensitive data in tickets] -> Treat content as data, use no tools, minimize transmitted content, and avoid payload logging. Provider data handling depends on its configuration and terms.

## Migration Plan

Apply a non-destructive versioned migration adding options and structured decision storage, seed defaults once, and preserve existing simulated results. Deploy API, worker, and SPA together after model configuration; pending jobs use the new worker, while old completed simulated jobs are not requeued. Back up retained data and document rollback: restore the prior application and schema only after accounting for structured decisions that the old schema cannot represent; never silently discard them.
