# Lumen

Lumen is a domain-agnostic ticket assistant in development. It stores tickets, suggests classifications, and drafts responses with optional knowledge-base context. People review, edit, and approve the final text; approval saves it and does not send a message.

The application uses a TypeScript SPA, a Python/FastAPI backend, and PostgreSQL with pgvector. Classification and response drafting use independently configured model roles. Use fictional data for development and demonstrations.

## Getting started

The managed local workflow requires Windows PowerShell 5.1, GNU Make, Python 3.13, [uv](https://docs.astral.sh/uv/), Node.js 24, npm, and Docker Desktop with Compose.

From the repository root:

```powershell
Copy-Item .example.env .env
# Edit .env: set the PostgreSQL password and initial administrator credentials.
make setup
make dev-start
```

Open [http://127.0.0.1:5173](http://127.0.0.1:5173) and sign in with the administrator credentials from `.env`. The launcher creates the administrator only when the database has no accounts; it does not overwrite existing credentials. The API listens on port 8000 by default. Ports and other settings are listed in `.example.env`.

Set `LUMEN_DECISION_MODEL` and `LUMEN_DECISION_API_KEY` to enable classification, and `LUMEN_RESPONSE_MODEL` and `LUMEN_RESPONSE_API_KEY` to enable response drafting. Semantic indexing also requires `LUMEN_EMBEDDING_API_KEY`. These integrations send relevant fictional ticket or document content to their configured providers and may incur charges. Keep credentials in the ignored `.env` file.

```powershell
make dev-status   # Show service status
make dev-logs     # Show recent logs
make dev-restart  # Restart managed services
make dev-stop     # Stop services; retain the database volume
```

The managed launcher uses the `lumen` Compose project across checkouts, which therefore share its local database. Keep a backup before migrations or rollback, and reuse the database credentials associated with an existing volume. Local authentication is intended for a trusted machine and network.

## Project structure

- `apps/web/` — TypeScript, HTML, and CSS frontend.
- `apps/api/` — FastAPI application, worker, and database migrations.
- `openspec/` — requirements and change records.
- `docs/` — product and development documentation.

## Documentation

- [Product vision](docs/product.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Agent-assisted development](docs/agentic-development.md)
- [Backend observability requirements](openspec/specs/backend-observability/spec.md)

Workspace API endpoints require an authenticated session; `/health` reports API process availability.
