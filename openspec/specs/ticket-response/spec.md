# ticket-response Specification

## Purpose

Allow an operator to write and review a durable manual response for a ticket before approving its final text.

## Requirements

### Requirement: Save a manual response
The system SHALL allow one nonblank manual response per existing ticket to be saved as a draft and retrieved later with its status and latest text-edit timestamp.

#### Scenario: Save and resume
- **WHEN** an operator saves nonblank text for a ticket and later reopens it
- **THEN** the saved text, draft status, and last edit time are available

#### Scenario: Invalid text or missing ticket
- **WHEN** a response is blank or its ticket does not exist
- **THEN** the system rejects the save without creating a response

### Requirement: Approve a response
The system SHALL allow a human operator to approve nonblank response text and persist exactly the approved text as approved without sending an external message.

#### Scenario: Approve edited text
- **WHEN** the operator approves the current editor text
- **THEN** that text and approved status are saved together
- **AND** no external message is sent

### Requirement: Edit an approved response
The system SHALL allow an approved response to be edited; saving changed text SHALL replace the stored text and return its status to draft until approved again.

#### Scenario: Correct an approved response
- **WHEN** changed text is saved from an approved response
- **THEN** the changed text is stored as draft and requires renewed approval

### Requirement: Record latest edit time
The system SHALL record and display the time of the latest persisted visible response text change, including initial creation. It SHALL retain original AI generation texts separately but need not maintain a history of previous visible response texts.

#### Scenario: Approval without a text change
- **WHEN** an existing response is approved without changing its text
- **THEN** its last text-edit timestamp remains unchanged

### Requirement: Protect response work
The system SHALL report save and approval failures without claiming success or discarding unsaved editor content. It SHALL prevent stale updates from silently overwriting a newer saved response.

#### Scenario: Concurrent edits
- **WHEN** an operator saves or approves a response based on an outdated version
- **THEN** the operation is rejected as a conflict and the editor retains the operator's text for recovery

#### Scenario: Background classification refresh
- **WHEN** classification status refreshes while the operator is editing
- **THEN** unsaved response text remains intact

#### Scenario: Leave with unsaved changes
- **WHEN** the operator attempts to leave an editor containing unsaved changes
- **THEN** the interface warns that those changes may be lost

### Requirement: Visually distinguish the response workspace
The ticket detail SHALL present the response editor in a distinct, visually emphasized container while retaining its status, save and approval controls.

#### Scenario: Review and edit a response
- **WHEN** an operator opens a ticket
- **THEN** the response workspace is visually distinct from the ticket description and exposes its existing editing actions

### Requirement: Review and adopt a suggestion
The system SHALL present generated suggestions separately from the editor and require an explicit operator action to adopt one into the visible response.

#### Scenario: Generation completes during editing
- **WHEN** a suggestion completes while the operator has unsaved text
- **THEN** the editor text remains unchanged and the suggestion is separately available for review

#### Scenario: Replace existing editor text
- **WHEN** an operator chooses to adopt a suggestion while the editor contains text
- **THEN** the system warns that the editor text will be replaced and requires confirmation before replacing it

#### Scenario: Stale response during adoption
- **WHEN** the saved response has changed since the editor's known revision
- **THEN** a save or approval is rejected as a conflict and the operator's editor text remains recoverable

### Requirement: Expose response provenance
The system SHALL distinguish a manual response from an adopted AI suggestion and an AI suggestion subsequently edited by a person, linking adopted suggestions to their preserved originals.

#### Scenario: Edit an adopted suggestion
- **WHEN** an operator edits and saves an adopted suggestion
- **THEN** the visible response changes, its AI-assisted origin is retained, and its original AI text remains unchanged

#### Scenario: Existing response
- **WHEN** a response created before this capability is viewed
- **THEN** it remains available with manual provenance and its text and status preserved

### Requirement: Readable response editor
The response editor SHALL present editable text with legible typography, spacing, and visible keyboard focus, and SHALL remain usable on narrow screens and in supported appearance themes.

#### Scenario: Review a multiline response
- **WHEN** an operator edits a long or multiline response
- **THEN** the text remains readable and editable without changing its content or existing save and approval behavior
