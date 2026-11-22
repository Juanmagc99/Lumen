# Spec Delta

## Purpose

Allow an operator to write and review a durable manual response for a ticket before approving its final text.

## ADDED Requirements

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
The system SHALL record and display the time of the latest persisted text change, including initial creation, and SHALL NOT maintain a history of previous response texts.

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
