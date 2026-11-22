# Proposal

## Why

The current workspace resembles a generic form rather than a distinctive ticket-review application. Navigation lacks prominence, filters are crowded and inconsistent, and operators cannot select multiple classification values.

## What Changes

- Give the workspace a coherent, expressive but restrained technological identity, with prominent navigation, clear active states, responsive layout, and support for light, dark, and system appearance.
- Reorganize the inbox around search, classification filters, a paired receipt-date range, active-filter feedback, and results. Move page-size selection alongside pagination.
- Replace native select menus in the workspace with accessible custom controls consistent with the existing appearance selector. Support multiple status, category, and priority selections.
- Extend ticket filtering end to end so selections within one dimension match any selected value, while different dimensions combine. Preserve existing single-value API clients and previously shared inbox URLs.
- Make classification options easier to scan, with deliberate inline editing and clear active and inactive states.

## Capabilities

### New Capabilities

- `workspace-navigation`: A recognizable, responsive workspace shell with accessible navigation and consistent custom selection controls.

### Modified Capabilities

- `ticket-browsing`: Multi-value filtering, paired date controls, active-filter visibility, and pagination placement and state preservation.
- `classification-options`: Scannable management of classification options with deliberate inline editing and visible status.

## Impact

The TypeScript SPA's shell, styles, inbox, classification-options view, selection controls, and URL state will change. The FastAPI ticket-list query contract, filtering domain, and database query will gain additive multi-value support; existing single-value requests remain supported. Existing appearance preferences, read-only ticket behavior, pagination, and historical inactive options remain supported. No new runtime dependency is assumed.
