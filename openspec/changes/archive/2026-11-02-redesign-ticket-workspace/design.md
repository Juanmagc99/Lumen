# Design

## Context

The SPA builds the shell and views in `apps/web/src/main.ts` and styles them in `style.css`. Its appearance selector is custom, while inbox filters use native selects and scalar hash parameters. The ticket API, domain filter object, and database predicates also accept one status, category, and priority each. See the proposal and delta specifications for the desired behavior.

## Goals / Non-Goals

**Goals:**
- Create a cohesive, restrained technological workspace that remains practical for frequent ticket review.
- Carry multi-value filtering consistently through UI state, shared URLs, API validation, database filtering, counting, and pagination.
- Reuse interaction patterns without adding a UI framework or unnecessary dependencies.

**Non-Goals:**
- Change classification decisions, ticket content, or human-review policy.
- Build a custom calendar popover: date fields remain keyboard-accessible native date inputs, visually grouped and sized consistently; their browser calendar may remain native.
- Introduce saved views, bulk ticket actions, or server-side user preferences.

## Decisions

### Workspace and visual language

Use a prominent desktop navigation rail that becomes an accessible compact navigation at narrow widths. Use a deep ink base, restrained blue accents, clear typography, deliberate spacing, and semantic status treatments; avoid decorative elements that compete with ticket content. Extend shared theme tokens to all surfaces, including dark and system modes. Indicate state with text or icons as well as color. Keep empty, loading, failure, and populated states intentional. A lightly restyled version of the current heading links was considered but would not resolve the weak workspace hierarchy.

### Inbox composition

Place search and classification selectors above results, group equal-sized start and end fields as one receipt range, and place page size with pagination, including when results are empty. Retain explicit Apply and Clear actions so a multi-selection can be composed before changing results. Display applied selections separately from pending edits; removing an applied chip immediately updates results and resets to page one. Changing page size applies only the already-applied filters. Dates retain inclusive UTC semantics and validation. Do not silently discard pending edits when page size changes; preserve them or clearly prompt the operator before they are lost.

### Selection controls

Build reusable, accessible custom selection primitives informed by the existing appearance menu. Status, category, and priority use multi-select checkable choices; page size and appearance use single selection. Support keyboard operation, visible focus, Escape, dismissal, selection announcements, long labels, scrolling, and options-loading or unavailable states. Preserve inactive classification options and label them. A styled native select was rejected because its popup remains platform-controlled. Avoid a custom date picker because it adds substantial accessibility and localization work beyond the agreed scope.

### API and URL compatibility

Keep existing `status`, `category_id`, and `priority_id` scalar query parameters and accept additive repeated plural parameters `statuses`, `category_ids`, and `priority_ids`. Validate each value, deduplicate, and take the union if both forms are supplied for a dimension. Within each dimension use OR; combine dimensions, search, and date bounds with AND before count and pagination. Explicitly include tickets without a classification when `unavailable` is one of the requested statuses. Preserve existing validation, inactive-option matching, deterministic ordering, and bounds. Do not fetch separate pages for each option and merge in the browser: it produces incorrect counts and pagination.

Read legacy scalar hash parameters and write a canonical repeated plural representation for multiple selections, retaining all applied state on return from detail. Keep page size and page in the URL. Unknown or malformed URL values must not silently turn into a broader, apparently successful filtered query; communicate invalid state and offer a recovery path. Keep existing single-value API clients working, and document mixed-form union behavior.

### Classification options

Render each category and priority as a readable row with text status and explicit edit and activation actions. Editing one row exposes a focused input with Save and Cancel, preserving error feedback and existing create, rename, activate, and deactivate semantics. Keep server validation authoritative.

## Risks / Trade-offs

- [Custom controls can regress accessibility] -> Implement keyboard and focus behavior deliberately and manually inspect it with assistive semantics and all supported themes.
- [A null classification needs special handling for mixed statuses] -> Combine the missing-classification predicate with selected job statuses using OR, then AND with other filters.
- [Old links or clients can lose filters] -> Retain scalar inputs, define mixed-form union behavior, and manually verify links and API requests across old and new forms.
- [A more expressive shell can crowd content] -> Check narrow and wide layouts, long values, populated and empty lists, and maintain usable contrast and focus.

## Migration Plan

Add the API's plural parameters while preserving scalar support, then deploy the SPA that uses them; no database migration is needed. Existing links continue to resolve. Roll back the SPA first if needed, then the additive API change; links using plural parameters require the updated API and SPA until restored or converted.
