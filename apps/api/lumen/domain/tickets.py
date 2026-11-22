"""Ticket and classification-option values shared by use cases."""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True)
class Option:
    id: UUID
    kind: str
    name: str
    active: bool
    color: str = "#64748B"


@dataclass(frozen=True)
class TicketView:
    id: UUID
    subject: str
    description: str
    received_at: datetime
    classification_status: str
    classification_result: str | None
    classification_source: str | None
    classification_categories: list[Option]
    classification_priority: Option | None
    classification_failure_reason: str | None
    effective_categories: list[Option]
    effective_priority: Option | None
    category_origin: str | None
    priority_origin: str | None
    classification_revision: int


@dataclass(frozen=True)
class TicketFilters:
    q: str | None
    status: str | None
    date_from: date | None
    date_to: date | None
    page: int
    page_size: int
    category_id: UUID | None = None
    priority_id: UUID | None = None
    statuses: tuple[str, ...] = ()
    category_ids: tuple[UUID, ...] = ()
    priority_ids: tuple[UUID, ...] = ()


@dataclass(frozen=True)
class TicketPage:
    items: list[TicketView]
    page: int
    page_size: int
    total: int


class StorageUnavailable(Exception):
    pass


class KeyConflict(Exception):
    pass


class DuplicateOption(Exception):
    pass


class ClassificationConflict(Exception):
    pass


class InvalidClassificationOption(Exception):
    pass
