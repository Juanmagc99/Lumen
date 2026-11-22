# Design

## Context

Tickets and classification jobs currently reference one manual and one model category respectively. A revision guards manual classification edits, and the worker validates active options again when finishing. The API and SPA use singular category fields. See the proposal for motivation.

## Goals / Non-Goals

**Goals:** Preserve existing assignments and provenance, support independent model and manual category sets, and retain safe concurrent updates and existing filtering semantics.

**Non-Goals:** Multiple priorities, profile-scoped options, changes to response approval, and a history of every model run.

## Decisions

1. Store model and manual category associations separately, with unique ticket/option pairs and an explicit manual-override marker. The marker distinguishes an intentionally empty manual set from no override. A single merged set cannot express that distinction or preserve model provenance. Keep priority and its existing override independently.
2. Replace category sets atomically under the existing classification revision and transactional locking. Retain currently effective inactive categories if submitted unchanged, but reject newly added inactive, duplicate, missing, or wrong-kind IDs. Worker completion revalidates all proposed IDs and updates only the model set; it never changes the manual set. A stale claim cannot write. This protects both operator edits and option deactivation races.
3. Request a category ID array and a nullable priority ID from the model. An empty array represents undetermined categories; malformed, duplicate, or invalid IDs fail the decision and follow existing retry handling. Keep the latest completed model set separate from the effective set; this is not a run history.
4. Use plural category collections in list/detail output and category writes, alongside explicit origin and revision. Treat this as an API breaking change rather than silently picking a single category; update the SPA and document the contract. Manual empty sets remain identifiable by origin. Existing scalar category filter query parameters remain supported; multiple values match any effective category. Use an existence predicate or equivalent to prevent duplicate tickets and inflated totals before pagination.
5. Display all effective tags and use an accessible multi-select in detail. Preserve inactive existing selections while allowing removal, and expose model suggestions in classification provenance. Keep existing unsaved response protection and category-independent priority editing.

## Risks / Trade-offs

- [Existing clients expect singular category fields] → Document the breaking contract and update the SPA together with the API.
- [Concurrent worker, edit, or option deactivation] → Lock and revalidate at commit; use revision conflicts for stale human writes and claim tokens for workers.
- [Many associations can duplicate filtered rows] → Filter using existence semantics and verify counts and pagination with overlapping categories.
- [Rollback may lose multiple or explicitly empty choices] → Refuse destructive downgrade while data cannot be represented; back up and export before any deliberate conversion.

## Migration Plan

Create association storage and the override marker, copy each existing non-null model and manual category into its respective set, preserve inactive IDs and revisions, and leave tickets without manual categories without an override. Retain simulated result provenance. Deploy the migration, API, worker, and SPA as a coordinated change; stop older workers during migration. Verify using isolated fictional data before applying to shared data. A downgrade is permitted only when all retained data can be represented without loss, otherwise stop and require an explicit backup and conversion.
