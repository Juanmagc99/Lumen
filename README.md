# Lumen

Lumen is a domain-agnostic ticket assistant in development. It stores tickets,
suggests classifications and drafts responses grounded in a managed knowledge
base. Operators review, edit and approve responses; approval saves the final
text and never sends a message. Decision and response models are configured
independently. Use fictional data for the local demo.

The frontend is a TypeScript SPA, the backend is a Python/FastAPI application,
and PostgreSQL stores application data and supports hybrid knowledge retrieval.
See [product vision](docs/product.md), [architecture](docs/architecture.md),
[roadmap](docs/roadmap.md), and [agent-assisted development](docs/agentic-development.md).

## Local authentication

For the local demo, set `LUMEN_ADMIN_USERNAME` and `LUMEN_ADMIN_PASSWORD` in the
ignored `.env` file. After applying migrations, `make dev-start` creates this
administrator only if there are no accounts. Existing accounts and passwords are
never overwritten on startup. A short password is accepted for this local-only
bootstrap; use the demo only on a trusted machine and network. These variables
are not sent to the API or worker processes. Losing the database also loses its
tickets, documents, and other data; this restores only the initial administrator.

Alternatively, after applying migrations, from `apps/api` run
`uv run python -m lumen.bootstrap.accounts bootstrap` to create the first account
interactively. To reset an existing administrator's password, use
`uv run python -m lumen.bootstrap.accounts recover`. Both commands require trusted local
host and database access and never accept passwords as command-line arguments.

The managed local launcher configures authentication for its loopback web origin.
For manual API startup, set `LUMEN_LOCAL_AUTH=true` and set
`LUMEN_PUBLIC_ORIGIN` to the exact local web origin, such as
`http://127.0.0.1:5173`. Outside local mode, set an HTTPS public origin and use
HTTPS; cookies are Secure and the server rejects other origins. Disable proxy
headers unless a trusted proxy is explicitly configured, and never trust client
forwarded headers. `LUMEN_SIGNIN_FAILURE_LIMIT` optionally sets the positive
failed-attempt limit (default 5 per 15 minutes).

## Requirements

- Python 3.13 and [uv](https://docs.astral.sh/uv/)
- Node.js 24 and npm
- Docker Desktop with Compose for the local PostgreSQL database

Keep the local database password in the ignored `.env` file. The database is bound to localhost and persists in the Compose volume.

## Setup (Windows PowerShell)

The development command interface requires Windows PowerShell 5.1 (`powershell.exe`) and GNU Make (3.81 or newer), in addition to the requirements above. From the repository root, `make help` lists the commands and `make setup` installs the locked API and web dependencies. The equivalent manual setup follows. The Makefile permits its local helper script to run for that process without changing the machine's execution policy.

Create `.env` from `.example.env` if it does not already exist, and set `LUMEN_POSTGRES_USER`, `LUMEN_POSTGRES_DB`, and `LUMEN_POSTGRES_PASSWORD` in that file. Then use `make dev-start`: it loads `.env`, starts the Compose database, applies migrations, and starts the API, classification worker, and web in the background. `make dev-status` shows API, worker, web, and database status, `make dev-logs` displays recent logs, and `make dev-stop` or `make dev-restart` stops or restarts managed services. Stopping retains the database volume. Repeat starts do not launch duplicate managed processes.

The default API and web ports are 8000 and 5173. Set `LUMEN_API_PORT` or `LUMEN_WEB_PORT` in `.env` to choose different ports. `LUMEN_POSTGRES_PORT` sets the PostgreSQL host port and defaults to 5432; PostgreSQL continues to listen on port 5432 inside its container. Use `make dev-stop` before changing ports, then `make dev-start`. Values in `.env` take precedence over the calling environment. Use `NAME=value` entries, with single quotes around values containing `#` or `$`; the file is data and is never executed as a script. Port conflicts are reported rather than terminated. Process metadata and logs are stored under the ignored `.lumen-dev/` directory; logs can contain local ticket data. Process records from before the last Windows boot are removed automatically, without deleting logs. If a process exits during the current boot or its identity cannot be verified, inspect the metadata and any remaining processes before manually removing the corresponding JSON file. Do not delete the runtime directory while services are running.

The tooling uses the Compose project name `lumen` in every checkout, so they share the same database and volume. Stopping that database affects every checkout using it. A volume belonging to a different Compose project is separate; no volume is migrated or deleted automatically. Reuse the password used when the selected volume was first initialized. See the lifecycle helpers in `scripts/dev.ps1` when adding another service.

From the repository root, install the locked API dependencies into a virtual environment:

```powershell
uv sync --project apps/api --locked --python 3.13
```

Docker Compose also loads the root `.env` when invoked directly. To start PostgreSQL manually:

```powershell
docker compose --project-name lumen up -d --wait postgres
```

The configured database, user, and password are initialized only when the volume is first created. Changing `.env` does not update existing roles or databases; reuse the existing settings or manage them explicitly. Stopping the container does not remove the volume.

The `make dev-start` command loads local settings and applies migrations. The backend centralizes database and worker settings in `apps/api/lumen/bootstrap/config.py`; database settings are validated when a connection is needed, so `/health` remains independent of database configuration. Manual API, worker, or migration sessions must export the database user, password, name, and optional port, or set `DATABASE_URL` separately with special characters URL-encoded; manual commands do not load `.env`. When supplied, `DATABASE_URL` takes precedence over the individual database settings.

The backend package is `apps/api/lumen`. Its `bootstrap` package composes the API and worker. The `lumen.bootstrap.worker` module connects the classification use case to PostgreSQL job operations and the LiteLLM decision adapter. The worker runner polls for work; model calls occur after the job claim is committed.

Before rolling back, back up the database and retain any structured classification decisions and option names: the older application cannot represent them. Migration `0004_classification_options` refuses to downgrade while model results or option references remain. Export and account for those decisions before removing them deliberately and restoring the prior application and schema. Rolling back earlier migrations can delete ticket data; retain a backup or the database volume when data is needed.

Migration `0005_ticket_responses` refuses to downgrade while responses remain. Back up and export response text before deliberately removing response records and downgrading; the previous schema cannot retain them.

Migration `0007_multiple_categories` preserves existing model and manual categories, including inactive options and revisions. Back up the database before upgrading, stop older API and worker processes, and deploy the migration, API, worker, and web application together. Before rollback, back up and export category assignments and their origins. The migration refuses to downgrade if a model or manual selection has multiple categories or a manual selection is explicitly empty; the older schema cannot represent those choices. Convert such data deliberately only after retaining a backup, then downgrade and restore the matching older application.

Hybrid retrieval requires the PostgreSQL `vector` extension. The local Compose database uses the pgvector PostgreSQL 17 image and retains the existing PostgreSQL 17 data volume; back up the database before changing images or applying migration `0014_hybrid_retrieval`. External PostgreSQL installations must provide the extension and allow the migration role to create it. Deploy the schema and matching application together. Migration `0014` preserves documents and citations. Before rollback, back up embedding data and retrieval audit; the downgrade refuses to discard recorded retrieval audit. The extension itself is left installed. Do not remove retained audit merely to force a downgrade.

The embedding provider is configured separately using `LUMEN_EMBEDDING_API_KEY`, `LUMEN_EMBEDDING_MODEL` (default `text-embedding-3-small`), `LUMEN_EMBEDDING_DIMENSIONS` (default 1536) and `LUMEN_EMBEDDING_TIMEOUT_SECONDS` (default 30, maximum 60). An existing OpenAI API key can be supplied for this role in the ignored `.env` file. OpenAI receives document fragments for indexing and ticket query text for semantic retrieval, and charges for embedding input usage; use fictional data only. Changing the model or dimensions requires compatible reindexing. A failed call can still incur charges, including on retry.

Configure the same embedding model and dimensions in the API and all workers. The document listing includes `semantic_status` and `semantic_failure_reason` for the active ready version, independently of ingestion status. `POST /api/knowledge/versions/{version_id}/semantic-retry` requeues a failed semantic indexing job and returns 409 when it is not failed. Incomplete indexing leaves lexical retrieval available. Generation attempts expose `retrieval_mode`, `retrieval_reason` and `embedding_input_tokens`; unavailable usage remains unknown. A lexical-only warning identifies when semantic search could not be used, including during backfill. Source citations and insufficient-evidence handling still require human review.

See [product vision](docs/product.md), [architecture](docs/architecture.md), [roadmap](docs/roadmap.md), and [agent-assisted development](docs/agentic-development.md).

Install and check the frontend:

```powershell
npm ci --prefix apps/web
npm run typecheck --prefix apps/web
npm run build --prefix apps/web
```

These commands match the foundation CI checks. CI installs the locked API dependencies and checks and builds the frontend; it does not run tests.

For the ticket inbox change, the frontend typecheck and production build completed successfully on Windows on 2026-10-29. No tests were created or run.

## Run locally

In one PowerShell terminal, start the API from the repository root:

```powershell
uv run --project apps/api --locked uvicorn lumen.bootstrap.api:app --app-dir apps/api --no-proxy-headers --host 127.0.0.1 --port 8000
```

In a second terminal, start the web development server:

```powershell
npm run dev --prefix apps/web
```

Open the URL printed by Vite. Its development proxy forwards `/health` and `/api` to the API on port 8000. To use a different API address, set `LUMEN_API_TARGET` in the Vite session before starting it. The indicator reports only API process availability, not database availability.

The production build contains static assets; serve `apps/web/dist` with a web server that falls back to `index.html` for SPA routes and forwards `/api` and `/health` to the API on the same origin. Run PostgreSQL and apply migrations separately before starting the API. Production deployment and secure external access remain outside this demo's scope.

## Submit a ticket

With the API running, send fictional content as JSON:

```powershell
$body = @{ subject = 'Example request'; description = 'A fictional request for review.' } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/api/tickets -Method Post -ContentType 'application/json' -Body $body
```

A successful response has HTTP status 201 and includes `id`, `subject`, `description`, and UTC `received_at`. Missing or whitespace-only fields produce a validation error. Storage failures return 503; creation is reported only after the database commit.

Clients may include an `Idempotency-Key` header containing 1–255 visible ASCII characters (no spaces). Repeating the same key and exact subject and description returns the original ticket with HTTP 200. Reusing it with different content returns 409. Keys are global and retained for the lifetime of their tickets; requests without a key create separate tickets.

`GET /api/tickets` returns `{ "items": [...], "page": 1, "page_size": 25, "total": 0 }`, ordered newest first with identifier descending as the tie-breaker. This replaces the former array response. Optional query parameters are `q` (case-insensitive literal title substring), `status` (`pending`, `processing`, `completed`, `failed`, or `unavailable`), `date_from` and `date_to` (inclusive UTC dates in `YYYY-MM-DD` format), `page` (positive integer), and `page_size` (1–100, default 25). Filters combine before counting and pagination. For example, `GET /api/tickets?q=example&status=completed&page=1&page_size=50`. Invalid values or reversed dates return 422; a page beyond the results is empty. Counts and pages reflect current data, so concurrent changes can shift results. The inbox offers page sizes 25, 50, 75, and 100. `GET /api/tickets/{id}` returns a ticket's full details or 404 when the identifier is unknown.

The list also accepts `category_id` and `priority_id` UUID filters, including inactive options. Repeated `statuses`, `category_ids`, and `priority_ids` parameters select multiple values, for example `?statuses=pending&statuses=failed`. Values in the same dimension match any value; different dimensions combine. A ticket matches a category if any effective category matches. The scalar and plural filter forms can be combined and their values are unioned; duplicates have no additional effect. Invalid statuses and UUIDs return 422. Completed model results include a category array and a priority object or null; an empty category array is undetermined. `classification_source` distinguishes model suggestions from retained simulated results. Failed details include a non-sensitive failure reason to help identify recovery steps.

## Manual ticket responses

### Knowledge and response suggestions

The Knowledge workspace supports named knowledge bases, direct text entry, and UTF-8 `.txt` and `.md` files. The default maximum source size is 1 MiB, configurable with `LUMEN_KNOWLEDGE_MAX_BYTES`. Each edit creates a new retained version; processing status and retry are visible. Deactivation excludes a source from new searches while retaining old versions. The worker processes content into indexed fragments. Retrieval combines lexical and semantic search when embeddings are available and falls back to lexical search otherwise. A selected knowledge base is not a security boundary.

In a ticket, select a knowledge base and choose **Generate response**. Requests are queued; suggestions, retrieved excerpts and available audit information appear separately from the response editor. **Use suggestion** replaces editor text only after confirmation when text is present. Review and save or approve the result. Approval never sends a message. The original generation remains stored separately when the visible response is edited. No matching source produces an explicit insufficient-evidence result without calling the model. A citation identifies a retrieved source; it does not prove that a claim is supported.

Configure the worker with `LUMEN_RESPONSE_MODEL`, `LUMEN_RESPONSE_API_KEY` and `LUMEN_RESPONSE_TIMEOUT_SECONDS` (default 60, maximum 120). These are separate from the decision model. Limits shared by response workers are `LUMEN_RESPONSE_CONCURRENCY` (default 2), `LUMEN_RESPONSE_RATE_LIMIT` (20 calls), `LUMEN_RESPONSE_RATE_WINDOW_SECONDS` (60), `LUMEN_RESPONSE_QUEUE_LIMIT` (100), `LUMEN_RESPONSE_MAX_ATTEMPTS` (3) and `LUMEN_RESPONSE_RETRY_SECONDS` (10). Limits and optional prices must be consistent across processes. Optional `LUMEN_RESPONSE_INPUT_PRICE_PER_MILLION`, `LUMEN_RESPONSE_OUTPUT_PRICE_PER_MILLION` and `LUMEN_RESPONSE_CURRENCY` must be supplied together; they provide an estimate for the configured model rather than provider billing. Missing usage or prices is shown as unknown. Failed or interrupted provider calls may still incur charges and may be repeated. The model provider receives the ticket and selected retrieved excerpts; use fictional data only. Store credentials in the ignored `.env` file.

For each suggestion, choose a knowledge base or explicitly choose to proceed without one. Without a base, no sources are consulted and the model may offer general guidance; verify its claims and missing details before use. It can still make mistakes despite its instructions. A base-backed request with no matching evidence does not fall back to general guidance. The migration permits source-free generation records and refuses downgrade while such records exist; deploy the updated schema before the API and worker.

`GET /api/tickets/{id}/response` returns `null` when no response exists, or an object containing `ticket_id`, `text`, `status` (`draft` or `approved`), `edited_at` (UTC) and `revision`. `PUT /api/tickets/{id}/response` saves text; `POST /api/tickets/{id}/response/approval` approves the supplied text. Both accept `{"text":"...","expected_revision":null}` for an absent response or the last observed positive revision for an existing response. They return the saved object, reject stale revisions with 409, blank text with 422, missing tickets with 404 and storage failure with 503. Save changed text after approval to return to draft; approve again to record the reviewed text. Approval itself does not send a message. The timestamp records the last saved text change, not approval alone; only the current text is retained.

## Checks performed

For on-demand grounded responses, an isolated PostgreSQL container was upgraded from the previous schema with a fictional ticket and approved response retained. Manual API and browser checks covered text and Markdown source creation, rejected inputs, document versions, deactivation, ingestion recovery, scoped lexical retrieval, source inspection, queued generation, insufficient evidence, duplicate requests, a configuration failure, rate admission, expired-claim rejection, response adoption, approval and concurrent edit recovery. A controlled in-memory provider response supplied fictional citations and usage for audit and cost inspection; an unknown citation was rejected. No real response-model provider call was made, and an actual worker process crash during a provider call was not reproduced. Frontend type checking and build completed. No tests were created, modified or run. The shared development database was not migrated during these checks.

For hybrid retrieval, an isolated pgvector PostgreSQL container retained a fictional document through upgrade, downgrade and re-upgrade. Manual checks covered existing and new document indexing, expired claims, version selection, deactivation, model changes, simulated semantic matches, keyword matches, unrelated content, base isolation, provider unavailability, incomplete indexing, recovery, citations, insufficient evidence and human approval without sending. A browser inspection covered indexing failure and retry, generation warnings and source audit. Vector and response providers were simulated; no real model-quality evaluation or real provider call was completed because no OpenAI key was available to the embedding adapter. The similarity cutoff is an initial heuristic, not a calibrated guarantee. The shared development database was not migrated. Frontend type checking and build passed; no tests were created, modified or run.

For multiple ticket categories, an isolated PostgreSQL container retained fictional manual and model associations, an inactive category and revision through upgrade; downgrade preserved representable values and refused multiple or explicitly empty manual selections. Controlled worker checks covered multiple and empty model results, duplicate and deactivated options, retry, and completion after a manual empty selection. Manual API checks covered concurrent and stale writes, category validation, inactive retention, independent priority, overlapping filters and populated pages. The workspace was inspected at desktop and narrow widths in light and dark appearances with fictional data, including simulated and inactive values, keyboard selection, conflict recovery, and unsaved response text during classification refresh. The real model provider and an actual worker process restart during a claim were not exercised. The shared development database was not migrated. No tests were created, modified or run.

For manual ticket responses, an isolated PostgreSQL database was migrated from the previous schema with a fictional ticket retained. Manual API and application checks covered blank and missing inputs, text and status transitions, last-edit time, concurrent creation, stale revisions, storage unavailability, API restart and persistence. The editor was inspected at desktop and mobile widths, including keyboard saving, markup-like text, unsaved navigation, background classification refresh, conflict recovery, and a failed save followed by a retry. Frontend typecheck and production build and strict OpenSpec validation passed. No tests were created, modified or run. The shared development database was not migrated during these checks.

During the hexagonal refactor, manual API checks against an isolated temporary PostgreSQL database covered creation, atomic rollback, idempotent replay and conflict, four concurrent requests with one key, unavailable storage, option validation and historical associations, combined filters, UTC date boundaries, literal wildcard search, ordering, pagination, detail, and classification retry. The worker was started and stopped against the same fictional data; see the classification notes below for provider and recovery limitations. The shared development volume was not modified for these checks. No tests were created or run.

The local command help, managed service status, migration discovery, and migrations on the isolated database were checked. Managed start, repeated start, stop, and restart were not exercised because the existing API, worker, web, and shared PostgreSQL service were already running; they were left undisturbed. The updated managed launcher and its worker-only decision settings were inspected, but their full process environment was not verified through a managed restart.

On Windows on 2026-10-29, the locked dependencies were reinstalled, PostgreSQL started in a separate Compose project, and the migration was applied to fresh databases. Manual API checks covered validation, unavailable storage, persistence across an API restart, idempotent replay and conflict, unkeyed creation, eight concurrent requests, list ordering, empty results, and missing tickets. The inbox and detail were inspected in a browser at desktop and mobile widths, including markup-like fictional content and loading, empty, missing, error, and retry states. `/health` returned `ok` when the configured ticket database was unreachable. The API and Vite used alternative ports because port 8000 was already occupied. No tests were created or run.

## Classification worker

Classification options are global and managed through `GET` and `POST /api/classification-options` and `PATCH /api/classification-options/{id}`. Both roles can read them; only administrators can change them. The API requires a local account for workspace operations and remains intended for a trusted demo environment, not untrusted networks. Options can be renamed or deactivated without removing historical associations. Names must be nonblank and unique within their type, ignoring case and surrounding whitespace.

An administrator creates and manages local user accounts through the workspace. Operators and administrators share tickets and knowledge; both can manage knowledge and approve response text without sending it. Accounts require no email service. Password resets revoke existing sessions, and the last active administrator cannot be removed. Authentication is a breaking change for previous anonymous API clients; `/health` remains public. When rolling back to an older API version, restrict network access because it does not enforce authentication.

Options also have a `color` in six-digit `#RRGGBB` form. It can be supplied on creation or updated with `PATCH`; omitting it on creation uses `#64748B`. Invalid colors are rejected. Existing options receive the same default during migration.

Ticket list and detail responses include `effective_categories` (an array), `effective_priority`, per-field `category_origin` and `priority_origin`, and `classification_revision`. `classification_categories`, `classification_priority`, and `classification_source` describe the latest model or historical simulated result separately. This replaces the former singular `effective_category` and `classification_category` fields. `PATCH /api/tickets/{id}/classification` accepts `expected_revision` and either or both of `category_ids` (the complete array) and `priority_id`; the former singular `category_id` write is no longer accepted. For example, `{"expected_revision": 2, "category_ids": ["<category-uuid>", "<another-category-uuid>"]}` replaces the category selection; `{"expected_revision": 3, "category_ids": []}` deliberately clears it. New selections must be active and of the matching kind; existing inactive categories can be retained or removed. A stale revision returns 409; invalid or duplicate options return 422. A manual category set, including an empty set, takes precedence over model suggestions during completion and retry. Category and priority filters match the effective values.

In the workspace, use **Tags** to manage category and priority names, colors, and activation. Ticket rows show their current tags; open a ticket and select **Edit** next to Categories to choose any number of categories using the checkboxes, then save. Clear every checkbox to save an intentionally empty manual selection. Previously assigned inactive categories are marked and can be retained or removed; they cannot be newly added. Edit Priority independently. Classification details identify the origin, processing state, and latest model category suggestions. The response area remains a manual review workspace: approving saves the text and does not send a message.

For the ticket tag workspace change, an isolated PostgreSQL database retained a fictional classification and inactive option through migration. Manual API and browser checks covered tag color creation and editing, invalid colors, inactive and wrong-kind selections, stale and concurrent updates, effective-value filters, simulated and undetermined results, and a controlled worker completion after a manual edit. The workspace was inspected in light and dark appearances at desktop and narrow widths; keyboard navigation, response draft preservation during classification refresh, and fictional response approval were checked. The browser pagination check changed page size with two tickets; it did not exercise multiple populated pages. No tests were created, modified, or run.

The worker's decision-model settings are `LUMEN_DECISION_MODEL` (a LiteLLM model identifier), `LUMEN_DECISION_API_KEY` (the provider credential), and `LUMEN_DECISION_TIMEOUT_SECONDS` (a positive integer, default 60). Set them in the ignored `.env`; never commit credentials. The timeout must leave more than ten seconds before the claim expires. These settings are independent of any future response model and are not required to accept tickets.

To run the worker manually from the repository root after exporting its database and decision settings, use `uv run --directory apps/api --locked python -m lumen.bootstrap.worker`. The development launcher passes the decision settings only to the worker process.

New tickets and pending classification jobs are committed together. The worker sends the ticket subject and description and the current active option names and identifiers to the configured model provider. Check the provider's data handling terms before supplying content. Calls may incur charges; a recovered or expired claim can cause another call, so model calls are not exactly once. No message is sent externally on behalf of a ticket.

The worker requests a JSON object with `category_ids` (an array of distinct category IDs, empty when undetermined) and `priority_id` (one ID or null), validates the IDs and records the suggestion. Historical simulated results remain labelled as simulated. Classification uses three attempts, a ten-second retry delay, and a 120-second claim expiry by default; set `LUMEN_CLASSIFICATION_MAX_ATTEMPTS`, `LUMEN_CLASSIFICATION_RETRY_SECONDS`, and `LUMEN_CLASSIFICATION_CLAIM_SECONDS` in `.env` to override these positive integers. Provider failures, invalid decisions, missing active options, and configuration problems do not produce simulated results. Correct the settings or options, restart the worker if its environment changed, and retry failed tickets from their detail view. `make dev-status` and `make dev-logs` include the worker.

## Classification checks performed

During the hexagonal refactor, manual checks against an isolated temporary PostgreSQL database covered pending work, concurrent claims, expired-claim recovery, rejection of a stale token, option deactivation during a claim, bounded provider failures, and manual and duplicate retry. Recovery was exercised by expiring a claim. A worker process was started and stopped; an unexpected real provider call used fictional ticket content because LiteLLM implicitly loaded the project's `.env`. The worker now disables this implicit loading, and a subsequent import confirmed that decision settings were not loaded automatically. An actual worker restart during a claim was not reproduced. No tests were created or run.

On Windows on 2026-11-02, an isolated PostgreSQL database was migrated with retained fictional simulated data. A fictional ticket created while the worker was stopped remained pending, then completed with a real configured model. A separate fictional ticket failed with invalid provider settings and completed after a manual retry with corrected settings. Manual inspections covered an expired claim and recovery, a stale token, a deactivated option, invalid output, a controlled timeout, and an explicitly undetermined result. The timeout and invalid-output scenarios used controlled responses; they were not observed from the live provider. Logs from the real call did not show the ticket payload or credential. Temporary data was isolated from the development volume. No tests were created or run.

On Windows on 2026-11-02, the migration was applied to the local PostgreSQL database. Manual checks covered atomic rollback, idempotent replay, processing with the worker initially stopped, simulated result persistence, concurrent claims, expired-claim recovery, rejection of stale claims, bounded failure, manual retry and duplicate retry. Managed start, repeated start, stop and restart were inspected. The inbox and detail were inspected at desktop and mobile widths, including the failure retry action. Temporary fictional tickets were removed afterward. The frontend typecheck and production build completed successfully. No tests were created or run.

## Inbox filtering checks performed

On Windows on 2026-11-02, manual checks with temporary fictional tickets covered combined filters, UTC day boundaries, missing classification records, literal wildcard search, pagination, API validation, page size selection, and returning from ticket details with filters and page preserved. The inbox was inspected at desktop and mobile widths; a background refresh preserved an edited input, and an API failure recovered on retry. Temporary tickets were removed. Frontend typecheck, production build, and strict OpenSpec validation completed successfully. Stale request handling was inspected in code; an out-of-order network response was not reproduced. No tests were created or run.
