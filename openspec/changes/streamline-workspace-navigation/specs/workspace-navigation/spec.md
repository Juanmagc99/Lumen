# Spec Delta

## MODIFIED Requirements

### Requirement: Navigate the workspace
The SPA SHALL provide prominent navigation to Inbox and Knowledge for both roles, and a visually separated administration section with Tags and Users for administrators. It SHALL identify the current destination visually and programmatically.

#### Scenario: Navigate between destinations
- **WHEN** a user opens an available workspace destination
- **THEN** the destination is shown as current and the other authorized destinations remain reachable

#### Scenario: Narrow viewport
- **WHEN** the viewport is narrow
- **THEN** authorized destinations remain accessible without horizontal page scrolling

### Requirement: Identify tag management
The workspace SHALL provide administrators a clearly named navigation destination for managing category and priority tags, using the existing classification options capability.

#### Scenario: Open tag management
- **WHEN** an administrator selects the tag management destination
- **THEN** the application opens the category and priority management view and identifies it as the current destination

## ADDED Requirements

### Requirement: Consolidate account actions
The workspace SHALL provide a single account control showing the signed-in identity and role and giving access to account settings, appearance, and sign-out. Account settings SHALL provide password change.

#### Scenario: Open account controls
- **WHEN** a signed-in user opens the account control
- **THEN** account settings, appearance, and sign-out are available without separate persistent header buttons

#### Scenario: Use the account control with a keyboard
- **WHEN** a user operates the account control with a keyboard
- **THEN** its options are reachable, focus is visible, and Escape dismisses the open menu and restores focus
