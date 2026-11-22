"""Values used by ticket classification."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID


@dataclass(frozen=True)
class ClassificationOption:
    id: UUID
    name: str
    kind: str


@dataclass(frozen=True)
class ClassificationDecision:
    category_ids: tuple[UUID, ...]
    priority_id: UUID | None


@dataclass(frozen=True)
class ClaimedClassification:
    ticket_id: UUID
    token: UUID
    subject: str
    description: str


@dataclass(frozen=True)
class ClassificationPolicy:
    max_attempts: int
    retry_seconds: int
    claim_seconds: int

    def exhausted(self, attempts: int) -> bool:
        return attempts >= self.max_attempts

    def retry_at(self, now: datetime) -> datetime:
        return now + timedelta(seconds=self.retry_seconds)

    def claim_expires_at(self, now: datetime) -> datetime:
        return now + timedelta(seconds=self.claim_seconds)


class ClassificationFailure(Exception):
    """A safe classification failure reason suitable for persistence."""
