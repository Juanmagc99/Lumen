## Purpose

Provide a recognizable and accessible workspace for navigating ticket review and classification configuration.

## ADDED Requirements

### Requirement: Navigate the workspace
The SPA SHALL provide prominent navigation between Inbox and classification options and identify the current destination visually and programmatically.

#### Scenario: Navigate between destinations
- **WHEN** an operator opens either workspace destination
- **THEN** the destination is shown as current and the other remains reachable

#### Scenario: Narrow viewport
- **WHEN** the viewport is narrow
- **THEN** both destinations remain accessible without horizontal page scrolling

### Requirement: Consistent custom selection controls
Workspace selection menus SHALL use a consistent custom appearance across supported themes and expose their labels, expanded state, available choices, and selections to assistive technology.

#### Scenario: Operate a selection menu with a keyboard
- **WHEN** an operator opens a selection menu using the keyboard
- **THEN** they can navigate choices, select them, close the menu with Escape, and perceive focus and selection

#### Scenario: Dismiss an open menu
- **WHEN** an operator dismisses a menu
- **THEN** it closes without losing previously selected values

### Requirement: Adapt workspace presentation
The workspace SHALL remain usable at narrow and wide viewport sizes and in System, Light, and Dark appearances, with legible controls and visible focus.

#### Scenario: Change appearance
- **WHEN** an operator changes appearance
- **THEN** navigation, selection menus, filters, and content reflect the selected appearance
