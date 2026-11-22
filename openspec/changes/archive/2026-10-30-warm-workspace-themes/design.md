# Design

## Context

The SPA uses plain TypeScript and CSS, renders a shared shell and list/detail states, and fetches the existing ticket API. See the proposal for motivation and the appearance preference spec for behavior.

## Goals / Non-Goals

**Goals:** Establish a cohesive, warm visual identity with moderate density, accessible appearance choices, and consistent treatment across responsive layouts and ticket states.

**Non-Goals:** Change ticket data or API behavior, introduce ticket editing, or build a general-purpose design system.

## Decisions

- Use Impeccable's operate-mode guidance when shaping the visual world: warm neutral light surfaces, a charcoal dark palette, restrained neutral accents, rounded forms, and a compact hierarchy. Reserve more saturated colors for meaningful status and future ticket labels. Precise visual choices remain for implementation and review. A purely decorative landing-page treatment would weaken the workspace's primary task.
- Define semantic CSS variables for surfaces, text, borders, accents, focus, and status in both themes. This keeps states consistent and avoids duplicating component styling; independent hard-coded colors would make contrast and maintenance harder.
- Provide a labeled three-choice control in the shared header. Store the selected mode in browser local storage, resolve System through the device preference, and listen for preference changes. Initialize the appearance early to minimize a flash of the wrong theme. Treat missing, invalid, or inaccessible storage as System and allow in-session changes when persistence fails. A server-side preference would add an unnecessary account and API dependency.
- Preserve semantic controls, text-safe ticket rendering, navigation, focus handling, and status feedback. Apply the design to list, detail, loading, empty, unavailable and missing states, including long content and narrow screens. Keep text and control contrast and visible keyboard focus in both palettes.
- Retain the existing stack and avoid adding libraries unless a concrete need emerges. Motion, if used, must be subtle and respect reduced-motion preferences.

## Risks / Trade-offs

- [Theme contrast or status colors become unclear] → Check text, controls, focus and status indicators in both themes; do not rely on color alone.
- [Local storage is unavailable or the preference is invalid] → Fall back safely and retain an in-memory selection for the session.
- [A spacious visual treatment reduces useful ticket density] → Review representative lists at desktop and mobile widths, including long subjects.
- [A visual redesign masks existing states or interactions] → Manually inspect the established read-only flow and error, empty and loading states.

## Migration Plan

No data migration is needed. The default follows the device; removing the frontend change restores the prior appearance and leaves any saved browser preference unused.
