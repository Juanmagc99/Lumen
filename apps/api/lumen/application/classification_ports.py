"""Dependencies of the classification use case."""

from typing import Protocol

from lumen.domain.classification import (
    ClaimedClassification,
    ClassificationDecision,
    ClassificationOption,
)


class ClassificationJobs(Protocol):
    async def claim(self) -> ClaimedClassification | None: ...

    async def active_options(self) -> list[ClassificationOption]: ...

    async def finish(
        self,
        claim: ClaimedClassification,
        decision: ClassificationDecision | None = None,
        failure_reason: str | None = None,
    ) -> None: ...


class DecisionModel(Protocol):
    def validate_configuration(self) -> None: ...

    async def decide(
        self,
        subject: str,
        description: str,
        categories: list[ClassificationOption],
        priorities: list[ClassificationOption],
    ) -> ClassificationDecision: ...
