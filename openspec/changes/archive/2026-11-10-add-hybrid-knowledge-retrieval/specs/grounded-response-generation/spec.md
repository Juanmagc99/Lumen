# Spec Delta

## ADDED Requirements

### Requirement: Combine lexical and semantic evidence
The system SHALL retrieve and combine lexical and semantic evidence from the selected knowledge base when semantic retrieval is available and its active content is fully indexed with the configured embedding model.

#### Scenario: Relevant paraphrase
- **WHEN** a ready active document contains relevant information expressed in different words from the ticket
- **THEN** semantic retrieval can include its fragment among the ranked evidence, subject to relevance and context limits

#### Scenario: Exact identifiers
- **WHEN** the ticket contains an identifier also present in a ready active document
- **THEN** lexical candidates remain eligible for the combined evidence

### Requirement: Disclose degraded retrieval
The system SHALL use lexical-only retrieval when semantic retrieval is unavailable or indexing is incomplete, and SHALL persist and visibly disclose this limitation with the generation outcome.

#### Scenario: Embedding provider unavailable
- **WHEN** the query embedding cannot be obtained
- **THEN** generation uses lexical evidence and identifies semantic retrieval as unavailable

#### Scenario: Incomplete index
- **WHEN** any active ready content in the selected base lacks compatible embeddings
- **THEN** generation uses lexical evidence and identifies semantic indexing as incomplete

#### Scenario: No lexical evidence during fallback
- **WHEN** degraded retrieval finds no useful lexical evidence
- **THEN** the result indicates insufficient evidence as well as the degraded retrieval mode
