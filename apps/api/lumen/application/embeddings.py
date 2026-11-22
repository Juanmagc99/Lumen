"""Embedding provider boundary and safe failure category."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EmbeddingBatch:
    vectors: tuple[tuple[float, ...], ...]
    input_tokens: int | None


class EmbeddingFailure(Exception):
    """A provider failure without sensitive request or response data."""


class EmbeddingProvider(Protocol):
    async def embed(self, texts: list[str]) -> EmbeddingBatch: ...
