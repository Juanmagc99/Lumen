# classification-options Specification

## Purpose

Allow operators to maintain global category and priority options for ticket classification and browsing.

## Requirements

### Requirement: Manage classification options
The application SHALL let operators list, create, rename, activate, and deactivate global category and priority options. Names SHALL be nonblank and unique within each option type, ignoring case and surrounding whitespace.

#### Scenario: Add an option
- **WHEN** an operator adds a valid category or priority
- **THEN** it is available for subsequent classification

#### Scenario: Duplicate or blank name
- **WHEN** an operator submits a blank or duplicate name in the same option type
- **THEN** the application rejects the change and explains why

#### Scenario: Deactivate an option
- **WHEN** an operator deactivates an option
- **THEN** it is excluded from new model decisions while existing ticket associations remain visible and filterable

#### Scenario: Rename an option
- **WHEN** an option is renamed
- **THEN** existing ticket associations retain their identity and show the current name

### Requirement: Seed initial options
The system SHALL initialize generic editable options once without replacing later operator changes.

#### Scenario: Initial setup
- **WHEN** the options are initialized for the first time
- **THEN** categories include Inquiry, Incident, Request, and Other and priorities include Low, Normal, High, and Urgent

#### Scenario: Repeated startup
- **WHEN** the system starts again after options were edited or deactivated
- **THEN** the operator's changes are preserved

### Requirement: Present classification options for review
The classification-options view SHALL present categories and priorities as scannable lists that distinguish active and inactive options with text, and SHALL expose actions to edit or change each option's status.

#### Scenario: Review options
- **WHEN** an operator opens classification options
- **THEN** each option's name and active or inactive status are visible without entering edit mode

### Requirement: Edit an option deliberately
The classification-options view SHALL enter a distinct editing state when the operator chooses to rename an option, and SHALL allow the operator to save or cancel the edit.

#### Scenario: Cancel an edit
- **WHEN** an operator changes a name in edit mode and cancels
- **THEN** the stored name remains unchanged and the view returns to the option list

#### Scenario: Reject an invalid edit
- **WHEN** an operator attempts to save a blank or duplicate name
- **THEN** the view preserves the edit and explains the validation error

### Requirement: Configure tag colors
Operators SHALL be able to set and change a color for each category and priority, with a readable name always shown alongside the color. Existing options SHALL receive a usable default color.

#### Scenario: Update a tag color
- **WHEN** an operator saves a valid color for an option
- **THEN** its current color is shown wherever that option is presented as a tag

#### Scenario: Invalid color
- **WHEN** a submitted color is unsupported
- **THEN** the application rejects it and preserves the existing color

#### Scenario: Readability
- **WHEN** tags are displayed in any supported appearance
- **THEN** their labels remain legible and color is not their only identifier
