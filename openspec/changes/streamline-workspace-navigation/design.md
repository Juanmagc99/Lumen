# Design

## Context

The shell and hash routing live in `main.ts`, while `auth.ts` injects separate account buttons into the header and maintains the current account. Tags is currently reachable by both roles, with editing controls hidden for operators. Users management is an administrator-only dialog. Appearance has a separate keyboard-accessible control. Knowledge management is currently shared by both roles.

## Goals / Non-Goals

**Goals:** Give role-aware navigation and account controls a coherent home, preserve accessible interaction and unsaved work, and make the shell feel like a compact working environment.

**Non-Goals:** Changing server permissions, changing Knowledge access, introducing profile fields, redesigning ticket workflows, or adding a UI framework.

## Decisions

- Group Inbox and Knowledge as workspace destinations and Tags and Users as administration destinations. Replace the Users header button with a destination that presents the existing management functionality in the workspace. This provides a clear current location and avoids adding another unrelated modal. Keep the existing Tags hash compatible.
- Share authenticated account state and role updates between authentication and navigation through a small explicit interface. Gate administrative views before rendering; if direct access is forbidden, present an access message and link to Inbox. On role demotion, close any administrative UI and move to a safe access state. Continue to rely on the server for authorization; a hidden link is not a security boundary. Do not discard unsaved response text when handling expiry or authorization failures.
- Place one account trigger at the bottom of the desktop sidebar and in a compact reachable position on narrow screens. Its menu contains account settings, appearance, and sign-out; account settings exposes the existing password change and identity, without inventing profile data. Preserve password and logout behavior, including the existing unsaved-work warning.
- Reuse the existing appearance selection, persistence, and system-following behavior inside the account experience. Support keyboard navigation, Escape, focus restoration, and dismissal; ensure nested controls do not trap focus or overlap off-screen.
- Reduce shell spacing and decorative copy, keep a restrained hierarchy, and turn service health into a discreet status with an intelligible failure state. Retain responsive behavior and light, dark, and system themes. Prefer adapting existing CSS and native controls over introducing dependencies.

## Risks / Trade-offs

- [Stale role after a server-side change] -> Refresh identity on existing authorization failures and update navigation and administrative views together; server checks remain authoritative.
- [Navigation or sign-out could interrupt an unfinished draft] -> Preserve existing dirty-work handling and avoid destroying editor state on authorization errors.
- [Account menu and small screens can make controls hard to reach] -> Provide visible focus, keyboard and pointer dismissal, and a layout that stays within the viewport.
- [Moving user management changes a familiar entry point] -> Label Users clearly in the administrative group and preserve all existing operations and feedback.

## Migration Plan

Ship as an SPA change with existing APIs and data. No data migration is required; rollback restores the previous frontend. Existing direct Tags links remain valid for administrators.
