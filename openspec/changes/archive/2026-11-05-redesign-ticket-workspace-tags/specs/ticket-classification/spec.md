# Spec Delta

## ADDED Requirements

### Requirement: Preserve manual classification choices
Each manually chosen category or priority SHALL take precedence over automated results for that field, including results already in progress or produced after retry. The other field SHALL remain eligible for automatic classification until manually chosen.

#### Scenario: Model completes after manual edit
- **WHEN** an operator changes a field while classification is processing and the worker completes
- **THEN** the manual value remains the current value and the other field can receive the valid model result

#### Scenario: Retry after manual edit
- **WHEN** classification is retried after a field was manually changed
- **THEN** the manual field remains unchanged

### Requirement: Retain classification provenance
The application SHALL distinguish current manual choices from model-generated and historical simulated results without presenting simulated results as real model decisions.

#### Scenario: Inspect origin
- **WHEN** an operator inspects classification provenance
- **THEN** the origin of current values and any available historical simulated result are clearly identified
