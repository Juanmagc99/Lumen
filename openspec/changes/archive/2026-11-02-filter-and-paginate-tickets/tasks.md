# Tasks

## 1. Filtered and paginated API

- [x] 1.1 Add validated query parameters and a paginated response contract; manually inspect defaults and validation failures for statuses, dates, ranges, pages, and sizes.
- [x] 1.2 Implement shared database filtering, counting, deterministic ordering, and bounded pages; manually verify combined filters, literal wildcard characters, UTC date boundaries, missing classifications, empty and out-of-range pages, and multiple pages using fictional tickets.
- [x] 1.3 Update README API documentation and examples for the breaking response and UTC dates; verify examples against the implemented contract.

## 2. Inbox controls and navigation

- [x] 2.1 Add accessible title, status, and UTC date controls, apply and clear actions, pagination with 25, 50, 75, and 100 items per page, and distinct empty states; manually inspect keyboard use, validation, desktop and mobile layouts.
- [x] 2.2 Preserve applied filters, page size, and page through detail navigation and browser history, handle stale requests and changing results, and retain background classification refresh without overwriting edits; manually inspect each behavior and request failure recovery.

## 3. Integrated verification

- [x] 3.1 Manually verify filtering across the complete collection before pagination and the full inbox-to-detail return journey with fictional data; report observations and limitations.
- [x] 3.2 Run frontend typecheck and production build, validate the OpenSpec change, and record checks performed; do not create or run tests without explicit user direction.
