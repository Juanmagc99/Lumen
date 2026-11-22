# Spec Delta

## MODIFIED Requirements

### Requirement: Present authorized actions
The workspace SHALL show the signed-in identity and role, provide sign-out, and expose only actions allowed for that role. The administration section and Tags and Users management destinations SHALL be visible only to administrators. It SHALL communicate authentication expiry and authorization failures without silently losing unsaved response text.

#### Scenario: Session expires during editing
- **WHEN** a protected save fails because the session has expired
- **THEN** the user is prompted to sign in again and unsaved response text remains recoverable

#### Scenario: Operator uses the workspace
- **WHEN** an operator signs in
- **THEN** Inbox and Knowledge are available and the administration section, Tags management, and Users management are not shown

#### Scenario: Direct administrative navigation
- **WHEN** an operator follows a direct link to Tags or Users management
- **THEN** the workspace does not display that management view and provides a clear access message and a route to an authorized destination

#### Scenario: Role changes during a session
- **WHEN** the workspace learns that the current user is no longer an administrator
- **THEN** administrative navigation and any open administrative view are removed and the user is offered an authorized destination
