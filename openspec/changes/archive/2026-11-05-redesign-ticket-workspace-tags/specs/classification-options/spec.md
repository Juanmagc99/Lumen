# Spec Delta

## ADDED Requirements

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
