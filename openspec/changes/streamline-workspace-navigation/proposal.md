# Proposal

## Why

The workspace mixes everyday navigation, administration, account actions, appearance, and service status across several prominent controls. This makes the interface feel fragmented and more editorial than a focused work tool.

## What Changes

- Separate everyday navigation from an administrator-only section containing Tags and Users; keep Inbox and Knowledge available to both roles.
- Consolidate identity, account settings, appearance, and sign-out under a single account control, with an appropriate compact layout on narrow screens.
- Make the workspace shell more compact and purposeful, reduce decorative copy, and present service status discreetly while keeping failures clear.
- Handle direct navigation and role changes consistently with the current server-enforced authorization, without changing Knowledge permissions.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workspace-navigation`: Organize destinations by role and distinguish workspace and administrative navigation.
- `role-based-access`: Restrict the Tags management destination to administrators and define behavior for direct access and role changes.
- `appearance-preferences`: Place the existing accessible appearance selection within the account experience.

## Impact

The SPA shell, navigation, authentication controls, account management presentation, styles, and responsive behavior are affected. Existing server authorization, authentication, appearance persistence, and shared Knowledge permissions remain in place; no new dependencies or API changes are planned.
