# Proposal

## Why

The inbox loads every ticket and offers no way to narrow the list. Search, filters, and bounded pages will make finding tickets practical as the inbox grows.

## What Changes

- Search ticket titles and combine classification status and receipt date filters across the complete collection.
- Return and display bounded pages, allowing 25, 50, 75, or 100 items per page and retaining the selected filters, page size, and page when returning from a ticket.
- **BREAKING:** Replace the ticket list API's unbounded array response with a paginated response and update the SPA and documentation together.
- Keep severity and category filters out of scope until structured classification data exists.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ticket-browsing`: Filter and paginate the ticket list through the API and inbox.

## Impact

The FastAPI ticket list contract and database query, TypeScript inbox, and API documentation change. Existing clients of the list endpoint must adapt to the new response shape. No additional service or dependency is required.
