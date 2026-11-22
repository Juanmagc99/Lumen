"""Values and errors for manually reviewed ticket responses."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ResponseView:
    ticket_id: UUID
    text: str
    status: str
    edited_at: datetime
    revision: int
    adopted_generation_id: UUID | None = None
    provenance: str = "manual"


class ResponseConflict(Exception):
    pass


class TicketMissing(Exception):
    pass


class InvalidGeneration(Exception):
    pass
