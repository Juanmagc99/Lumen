# Architecture

## Implemented

```text
TypeScript / HTML / CSS SPA
              | HTTP
              v
      FastAPI HTTP adapter                  Worker runner
              |                                  |
              +------------+---------------------+
                           v
                 Application use cases
                   |              |
                ports          decision port
                   |              |
                   v              v
           PostgreSQL adapter   LiteLLM adapter
                   |
          tickets, options, durable jobs
```

`apps/api/lumen/domain` contains domain values and classification policy; `application` owns use cases and ports. Inbound adapters translate HTTP or poll for work. Outbound adapters handle SQLAlchemy persistence and LiteLLM inference. `bootstrap` supplies process settings and composes the concrete adapters. Domain and application code do not import these frameworks or concrete adapters.

Ticket creation and its pending classification job commit together. Workers claim jobs with expiring tokens and PostgreSQL locks, commit before inference, and recheck claim ownership and selected options before completion. Retries are bounded; a recovered claim can still produce a repeated model call. Historical simulated results remain labelled; a provider failure does not generate a simulated replacement.

Database and model settings are read when needed, so `/health` reports API process availability without requiring a database or provider. The decision role is configured independently and its credential stays server-side. Tickets and option text are untrusted data; model output is validated. No external message is sent on behalf of a ticket.

PostgreSQL runs through the local Compose setup, and Alembic maintains its schema. The API and worker currently use bounded sessions and dispose each session's engine. See the README for setup, configuration, launch commands, and checks.

The HTTP boundary checks local opaque sessions and current account roles before workspace operations. PostgreSQL stores password hashes, session digests and sign-in counters; administrators manage accounts without email. Operators and administrators share all workspace data. The public health endpoint remains database independent, and workers do not use browser sessions. This local access control is not a secure multitenant or production deployment boundary.

Knowledge bases, document versions and chunk ingestion are persisted in PostgreSQL. The worker recovers ingestion claims and indexes fragments using PostgreSQL full-text search; retrieval uses only the latest ready version of active documents within the selected knowledge base. This is lexical retrieval and selection is not an authorization boundary.

An explicit ticket action creates a durable response generation job. Response workers coordinate call concurrency and request windows through database reservations, use a separately configured response model, validate returned citation identifiers against retrieved chunks, and record attempts, source versions, available usage and estimated costs. Source content and tickets are untrusted. An expired claim cannot commit a result, but provider calls can be repeated after an ambiguous interruption. A citation is not proof that it supports a claim.

Generated originals are retained separately from the current visible response. An operator can adopt and edit a suggestion, and the response links to the adopted generation for provenance. The existing optimistic revision prevents stale saves from silently overwriting newer work. Approval saves the visible text without sending a message.

## Proposed

Future capabilities may include profile management, semantic retrieval, extractable-text PDF support, and richer observability. A LangGraph workflow and vector search remain candidates rather than implemented dependencies.

Model choice, additional decision boundaries, checkpoint persistence, retention policy and deployment remain open. Add infrastructure only for a concrete responsibility.
