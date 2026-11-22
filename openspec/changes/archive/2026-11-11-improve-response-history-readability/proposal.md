# Proposal

## Why

Generated suggestions and their diagnostics accumulate in a dense list, making individual responses difficult to review. Text entry in the response and knowledge workspaces also lacks a consistent, comfortable reading experience.

## What Changes

- Separate generation history into identifiable, expandable entries, with the newest entry initially open and older entries initially collapsed.
- Improve the readability of suggestion text and the response and knowledge text editors while preserving original text, warnings, sources, and existing actions.
- Keep the interface usable with keyboard navigation, on narrow screens, and in both appearance themes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `grounded-response-generation`: Make individual generation outcomes and their review information easy to distinguish and inspect.
- `ticket-response`: Provide a readable response editing experience while preserving review and adoption behavior.
- `knowledge-management`: Provide readable text entry for adding and replacing knowledge content.

## Impact

The SPA's ticket response and knowledge views and styles are affected. Existing data, APIs, generation behavior, and dependencies remain unchanged.
