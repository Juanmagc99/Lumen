# Tasks

## 1. Multi-value ticket filtering

- [x] 1.1 Extend ticket-list query validation and domain filters with additive plural parameters, legacy scalar compatibility, and mixed-form union; verify valid, duplicate, invalid, and legacy requests manually and document the query contract.
- [x] 1.2 Update database predicates to OR values within a dimension, handle unavailable classifications, and AND dimensions before count and pagination; verify combined filters, inactive options, ordering, totals, and page boundaries with fictional data.

## 2. Workspace shell and controls

- [x] 2.1 Create the responsive navigation shell and theme tokens with restrained technological styling; inspect active navigation, readability, focus, and narrow and wide layouts in light, dark, and system appearances.
- [x] 2.2 Implement reusable custom single- and multi-selection controls based on the appearance pattern; manually verify keyboard navigation, focus return, Escape, selection announcements, long labels, and loading and unavailable states.

## 3. Inbox experience

- [x] 3.1 Extend hash state parsing and serialization for multiple selections while preserving legacy links and handling malformed values visibly; verify navigation to detail and back restores the full applied state.
- [x] 3.2 Reorganize search, multi-select filters, grouped equal-sized UTC date fields, applied chips, and clear/apply actions; verify draft and applied selections, individual removal, date validation, and empty or unavailable option states.
- [x] 3.3 Move page-size control beside pagination while preserving applied filters and pending edits; verify page resets, empty results, out-of-range pages, and all available page sizes.
- [x] 3.4 Refine ticket rows, status treatments, and loading, empty, no-match, and failure states; inspect populated and empty inboxes with fictional data at narrow and wide sizes.

## 4. Classification options

- [x] 4.1 Present categories and priorities as readable rows with text status and deliberate edit/save/cancel actions; manually verify create, rename, duplicate and blank errors, cancellation, activation, and deactivation.

## 5. Integrated review

- [x] 5.1 Build the SPA and manually review the complete navigation, filters, ticket detail return, options management, accessible control behavior, and supported appearances; report checks performed and any gaps without creating, modifying, or running tests.
