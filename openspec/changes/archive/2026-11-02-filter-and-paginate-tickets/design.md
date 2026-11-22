# Design

## Context

The current endpoint returns an unbounded array, and the SPA fetches it on each inbox render. Classification stores a job status and a fixed simulated result, not structured severity or category. See the proposal and ticket-browsing delta for scope and behavior.

## Goals / Non-Goals

**Goals:** Bound database and response work per page, apply filters consistently to the count and items, and make navigation recoverable across detail views.

**Non-Goals:** Full-text ranking, severity classification, snapshot isolation across requests, and new infrastructure.

## Decisions

1. Extend `GET /api/tickets` with `q`, `status`, `date_from`, `date_to`, `page`, and `page_size`; return `{items, page, page_size, total}`. Validate status against pending, processing, completed, failed, and unavailable. The last represents tickets without a job, matching current display behavior. Empty or whitespace-only search is treated as absent. This intentionally breaks the old array contract; update the SPA and documentation together instead of retaining an unbounded legacy response.
2. Use a shared predicate for count and page queries, with a left join for status, parameterized escaped case-insensitive substring matching, and UTC half-open timestamp bounds for inclusive date inputs. Filtering and ordering happen in PostgreSQL before limit and offset. Date controls explicitly identify UTC, avoiding ambiguity with the existing locally formatted timestamps. A full-text index and search service are unnecessary for this scope.
3. Use numbered offset pages of 25 by default, capped at 100, with stable timestamp and UUID ordering. The inbox offers page sizes 25, 50, 75, and 100; changing size resets to page one and preserves the filters. Offset pages support simple previous/next and total counts; concurrent inserts or status changes can shift results between requests, so pages are not a fixed snapshot. Cursor pagination would reduce shifting but complicates arbitrary page restoration and counts.
4. Store applied filter, page size, and page state in the inbox hash route and preserve it in detail navigation and the back link. Validate route input, retain controls during loading and errors, guard against stale asynchronous responses, and preserve existing periodic classification refresh. Do not replace actively edited control values during background refresh. Reset to page one on applying filters; clamp an emptied out-of-range page based on the returned total.

## Risks / Trade-offs

- [Count and offset queries become expensive at large scale] → Bound page sizes and revisit indexing or cursor pagination with evidence of need.
- [Concurrent changes shift results or counts] → Stable ordering limits ambiguity; document that each request reflects current data, not a snapshot.
- [UTC date selection differs from local display] → Label the date filter clearly and verify boundaries explicitly.
- [API consumers expect an array] → Document the breaking response and release API and SPA together.

## Migration Plan

No data migration is required. Deploy the API and SPA together and update list consumers to read `items` and pagination metadata. Roll back both together if needed; existing ticket data remains compatible.
