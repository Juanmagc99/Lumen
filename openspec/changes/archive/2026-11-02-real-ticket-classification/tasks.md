# Tasks

## 1. Options and retained data

- [x] 1.1 Add a non-destructive migration for global category and priority options, stable IDs, uniqueness, active state, structured decisions, and one-time default values; manually inspect upgrade and documented rollback while preserving existing simulated data.
- [x] 1.2 Implement option management API and document its local-only, unauthenticated scope; manually verify create, rename, deactivate, reactivate, duplicate and blank-name handling and historical references.
- [x] 1.3 Add option management to the SPA with clear empty, loading, error, and confirmation feedback; manually inspect desktop and mobile interactions and inactive options.

## 2. Real model classification

- [x] 2.1 Add and lock LiteLLM and configurable decision-model credentials and timeout; update credential-free configuration examples and documentation, then manually inspect missing and valid configuration without printing secrets.
- [x] 2.2 Replace the worker simulator for new work with a model call using active option IDs, structured validation, explicit undetermined outcomes, and untrusted input handling; manually inspect a real request with fictional data and verify no payload or secrets appear in logs.
- [x] 2.3 Preserve claim fencing and bounded retries, revalidate option activity atomically before committing, and distinguish provider failure from undetermined; manually inspect timeout, invalid output, changed options, stale claims, and recovery.
- [x] 2.4 Document provider data transfer, possible duplicate calls and charges, model selection, and recovery from configuration errors; verify documentation matches the actual configuration.

## 3. Ticket browsing

- [x] 3.1 Extend API responses and paginated filtering for category and priority while preserving existing filters and simulated result labels; manually inspect combined filters, counts, inactive options, and undetermined results.
- [x] 3.2 Update the inbox and detail to show decision suggestions and offer category and priority filters; manually inspect pagination state, historical simulated results, empty and error states at desktop and mobile widths.

## 4. Integrated verification

- [x] 4.1 With fictional tickets, manually inspect atomic intake with the worker stopped, subsequent real classification, provider failure, retry, and retained historical data; record outcomes and limitations.
- [x] 4.2 Run appropriate non-test frontend type/build checks and OpenSpec validation, and report results without creating or running tests.
