"""Port for retrieval of versioned evidence."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class Evidence:
    chunk_id: UUID
    version_id: UUID
    document_id: UUID
    document_name: str
    version: int
    excerpt: str


@dataclass(frozen=True)
class RetrievalResult:
    evidence: list[Evidence]
    mode: str
    reason: str | None = None
    input_tokens: int | None = None


class Retriever(Protocol):
    async def retrieve(self, base_id: UUID, query: str, limit: int = 8) -> RetrievalResult: ...
