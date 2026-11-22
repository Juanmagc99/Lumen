# Spec Delta

## ADDED Requirements

### Requirement: Configure the decision model securely
The development environment SHALL allow the worker's decision model and provider credential to be configured independently of any response model. Credentials SHALL remain server-side, outside version control and logs.

#### Scenario: Worker is configured
- **WHEN** an operator supplies a supported model identifier and required local credential
- **THEN** the worker uses that configuration for real classification

#### Scenario: Missing or invalid configuration
- **WHEN** required decision-model configuration is missing or invalid
- **THEN** the operator receives an actionable error without exposing credentials
- **AND** ticket intake does not depend on the provider being available
