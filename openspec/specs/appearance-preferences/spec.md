# appearance-preferences Specification

## Purpose

Let operators choose a comfortable workspace appearance that follows their device or reflects their preference.

## Requirements

### Requirement: Select appearance
The SPA SHALL provide an accessible, visible control to select System, Light, or Dark appearance and indicate the selected choice.

#### Scenario: Explicit appearance
- **WHEN** an operator selects Light or Dark
- **THEN** the selected appearance is applied throughout the workspace immediately

#### Scenario: Keyboard operation
- **WHEN** an operator uses the appearance control with a keyboard
- **THEN** they can identify and select each choice and perceive focus and selection

### Requirement: Follow system appearance
The SPA SHALL default to System when no valid saved preference exists and follow changes to the device appearance while System is selected.

#### Scenario: Device preference changes
- **WHEN** System is selected and the device switches between light and dark
- **THEN** the workspace updates to match without requiring a reload

#### Scenario: Explicit choice remains selected
- **WHEN** Light or Dark is selected and the device appearance changes
- **THEN** the workspace retains the explicit choice

### Requirement: Remember appearance
The SPA SHALL remember a valid appearance choice in the browser across reloads and later visits when local storage is available.

#### Scenario: Return visit
- **WHEN** an operator reloads after selecting an appearance
- **THEN** the saved choice and its appearance are restored

#### Scenario: Storage unavailable
- **WHEN** the browser cannot read or save the preference
- **THEN** the workspace remains usable and the operator can change appearance for the current session
