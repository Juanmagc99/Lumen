# Spec Delta

## MODIFIED Requirements

### Requirement: Record latest edit time
The system SHALL record and display the time of the latest persisted visible response text change, including initial creation. It SHALL retain original AI generation texts separately but need not maintain a history of previous visible response texts.

#### Scenario: Approval without a text change
- **WHEN** an existing response is approved without changing its text
- **THEN** its last text-edit timestamp remains unchanged

## ADDED Requirements

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
