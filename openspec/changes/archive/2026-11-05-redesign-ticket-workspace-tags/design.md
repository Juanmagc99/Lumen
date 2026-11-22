# Design

## Context

See the proposal and delta specs. Today the classification job owns one category and priority, their result source, and its status. The options API has name and active state but no color. List filtering reads classification associations, while detail refresh replaces the classification section without disturbing the response editor.

## Goals / Non-Goals

**Goals:** Provide durable per-field manual overrides, keep worker and human changes safe under concurrency, retain existing data and API consumers where practical, and create a coherent responsive tag presentation.

**Non-Goals:** Multiple category assignment, free-form arbitrary tags, removing classification progress, response generation, external message delivery, or a new dependency solely for tag rendering.

## Decisions

1. Keep automated results and current manual overrides separately. Add per-field override state and values to ticket-owned persistence, with an edit revision; current effective values select the manual override when present and otherwise the job result. This prevents a worker commit from erasing human changes and preserves model provenance. Do not overload a nullable value to mean both no override and an explicit cleared value; this change selects active values and does not add a clear-override action. Alternative: mutate the job result directly, which creates race and provenance ambiguity.
2. Offer a revision-checked ticket classification update API and return effective tags and per-field origins in list and detail. Retain existing fields and meanings for API compatibility; add explicit effective values rather than silently changing legacy model-result fields. Filtering must use the same effective values displayed. A stale write returns a conflict and leaves current choices intact; options must be active and of the correct kind at commit time. Existing inactive associations remain readable and filterable. Lock or otherwise atomically validate option state and revision.
3. Store a validated six-digit RGB color per option with a stable neutral default for migrated rows and new values when omitted. Use the color as a visual accent with theme-aware contrast, not as unvalidated CSS or the sole means of identification. Rename or recolor applies to all references because options retain identity. An unconstrained free-form CSS value is rejected.
4. Reuse the existing options workspace and route; add tag colors and rename its navigation label while retaining old links. Put category and priority on distinct detail rows near metadata; render category as a wrapping tag container but retain the single-category contract. Display provenance discreetly and provide explicit pending, processing, failed, undetermined and simulated states and retry where relevant. Preserve list filters, pagination and response draft state across refresh and navigation.
5. Make response a clearly differentiated region, not a new response workflow. Existing concurrency, unsaved-change warnings, approval and no-send semantics remain intact. Ensure keyboard operation, visible focus, accessible labels, and readable light and dark themes on narrow screens.

## Risks / Trade-offs

- [Stale updates or worker races] -> Revision checks and independent override persistence make updates atomic; validate with manual concurrency and in-flight worker checks.
- [Migration or changed filtering affects existing tickets] -> Retain existing job values, migrate defaults without modifying associations, and check effective-value filtering against old and new tickets.
- [Colors reduce readability] -> Constrain representation, apply accessible foreground/contrast treatment and keep text labels.
- [Future multiple categories] -> Treat the wrapping row as presentation preparation only; a later change must define storage, filters and model semantics rather than assuming this change implements them.

## Migration Plan

Add an Alembic migration for option colors and manual override state with compatible defaults. Existing classifications remain the fallback and retain source information. Deploy API and worker together before relying on the new UI. Rollback requires preserving or exporting manual overrides and colors before reverting their schema; otherwise those new values would be lost. Do not discard ticket, job or response data.
