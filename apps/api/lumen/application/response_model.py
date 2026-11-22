"""Response drafting port and validated result."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from lumen.application.retrieval import Evidence


class ResponseModelFailure(Exception):
    pass


@dataclass(frozen=True)
class GeneratedResponse:
    text: str
    rationale: str
    citations: tuple[UUID, ...]
    insufficient_evidence: bool
    reported_model: str | None
    request_id: str | None
    input_tokens: int | None
    output_tokens: int | None


class ResponseModel(Protocol):
    def validate_configuration(self) -> None: ...
    async def generate(self, subject: str, description: str, evidence: list[Evidence]) -> GeneratedResponse: ...
