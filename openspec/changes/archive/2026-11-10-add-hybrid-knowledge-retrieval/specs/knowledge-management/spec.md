# Spec Delta

## ADDED Requirements

### Requirement: Index knowledge for semantic retrieval
The system SHALL index active ready knowledge content for semantic retrieval across all knowledge bases, including content that existed before this capability was deployed.

#### Scenario: Existing content
- **WHEN** the capability is deployed with existing ready documents
- **THEN** their active versions are scheduled for semantic indexing without requiring operators to upload them again

#### Scenario: Updated document
- **WHEN** a replacement version becomes ready
- **THEN** it is scheduled for semantic indexing and superseded content is excluded from new retrievals

### Requirement: Show and recover semantic indexing
The system SHALL expose semantic indexing progress and failures separately from document ingestion and allow failed indexing to be retried without losing lexical search or historical citations.

#### Scenario: Provider failure
- **WHEN** semantic indexing fails
- **THEN** the failure is visible, the active document remains available for lexical retrieval, and an operator can retry indexing

#### Scenario: Embedding configuration changes
- **WHEN** the configured embedding model or vector dimensions change
- **THEN** incompatible existing embeddings are not used and active content is scheduled for reindexing
