# Spec Delta

## Purpose

Provide a basic way to check whether the Lumen API process is running without claiming that external dependencies are available.

## ADDED Requirements

### Requirement: API availability check

The API SHALL provide an availability check through `GET /health` without requiring model credentials or external services.

#### Scenario: API is running

- **WHEN** a client requests `GET /health` from a running API instance
- **THEN** the API returns HTTP 200 and a JSON object with `status` equal to `ok`

### Requirement: Scope of availability check

The availability check SHALL represent only the API process and MUST NOT claim that a database, model or worker is available.

#### Scenario: External dependencies are not configured

- **WHEN** a client requests availability without a configured database or AI provider
- **THEN** the response describes API availability only
