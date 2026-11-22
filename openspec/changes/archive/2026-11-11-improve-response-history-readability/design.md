# Design

## Context

The ticket view builds generation entries in `main.ts`, rebuilding the list on each status refresh. Each entry currently displays its full text, warnings, and audit disclosure in sequence. The shared content style preserves line breaks but constrains height; knowledge textareas have little dedicated styling. See the proposal and delta specs for the desired behavior.

## Goals / Non-Goals

**Goals:** Improve scanning and reading while retaining review context, editor state, and native keyboard interaction.

**Non-Goals:** Change generation, knowledge ingestion, persistence, response approval, or add a UI framework.

## Decisions

- Use independently expandable native disclosure entries with a clear status and date header. Initially open the newest by creation time, irrespective of API ordering, and allow multiple entries to be open. This reduces visual density without forcing comparison into a single-open accordion.
- Keep expansion state keyed by generation ID across polling updates, initialize unseen entries predictably, and avoid disrupting keyboard focus or nested source disclosures during refresh. A newly requested generation should be visible; previously chosen states remain intact. Rebuilding everything without preserving state would interrupt review.
- Give each entry its own spacing and surface, distinguish warnings, suggestion text, adoption action, and audit details, and retain all existing evidence and failure messages. Keep warnings associated with the relevant entry and expose them when it is opened; do not summarize or alter stored AI text.
- Use readable proportional typography, line height, padding, wrapping, and theme tokens for suggestion text and both kinds of textarea. Preserve whitespace and safe text rendering; avoid interpreting generated text as HTML or Markdown. Prefer ordinary page scrolling for long suggestions over a nested fixed-height text area, with long unbroken strings wrapping within the viewport.
- Reuse existing CSS conventions and native controls, including visible focus and responsive sizing. A new dependency or global redesign would add complexity outside this scope.

## Risks / Trade-offs

- [Collapsed entries can conceal important warnings] -> Identify status in the header and keep all warnings prominent within the expanded entry; never remove source or audit access.
- [Polling can interrupt inspection] -> Preserve disclosure and focus state, including nested audit and source disclosures, when updates arrive.
- [Long text can make the page tall] -> Collapse older entries and use page scrolling instead of nested scrolling.

## Migration Plan

Ship as a frontend-only change using existing records and endpoints. No migration is required; reverting the frontend restores the previous presentation.
