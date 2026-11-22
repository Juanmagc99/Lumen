## ADDED Requirements

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
