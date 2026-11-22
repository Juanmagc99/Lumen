# Proposal

## Why

The backend mixes HTTP handling, SQLAlchemy persistence, job coordination, and LiteLLM calls, making changes difficult to isolate and reason about. Establish clear hexagonal boundaries before adding more workflows and model roles.

## What Changes

- Organize the existing backend around domain concepts, application use cases and ports, inbound HTTP and worker adapters, outbound PostgreSQL and decision-model adapters, and explicit composition.
- Separate the LiteLLM integration and classification orchestration from the worker process while retaining the existing queue, failure handling, and security boundaries.
- Move ticket and classification-option operations out of HTTP handlers and keep persistence concerns in PostgreSQL adapters.
- Correct the local configuration loader so the documented decision-model settings reach the worker without being passed to the API or web process.
- Implement and verify the transition in reviewable phases, preserving existing API contracts, data, configuration, and operational behavior.
- Update backend architecture and development documentation to reflect the resulting implementation.

## Capabilities

### New Capabilities

None. The loader correction implements the existing local-development requirement; no new product capability is introduced.

### Modified Capabilities

None. Existing specifications remain the behavioral contract, including ticket intake, browsing, classification, classification options, service health, and local development.

## Impact

Backend Python modules, dependency composition, FastAPI and worker entry points, database session lifecycle, Alembic imports, development scripts, and architecture documentation may change. PostgreSQL, SQLAlchemy, FastAPI, LiteLLM, the existing schema and data, API responses, and environment variables remain in place; no new infrastructure or runtime dependency is required. The frontend is outside scope except for any strictly necessary compatibility correction.
