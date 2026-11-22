"""Ticket and classification-option use cases."""

from __future__ import annotations

from uuid import UUID

from lumen.application.ticket_ports import TicketStore
from lumen.domain.tickets import Option, TicketFilters, TicketPage, TicketView
from lumen.domain.responses import ResponseView


class Tickets:
    def __init__(self, store: TicketStore):
        self.store = store

    async def get_response(self, ticket_id: UUID) -> ResponseView | None:
        return await self.store.get_response(ticket_id)

    async def save_response(self, ticket_id: UUID, text: str, expected_revision: int | None, approve: bool, adopted_generation_id: UUID | None = None, provenance_supplied: bool = False) -> ResponseView:
        if not text.strip():
            raise ValueError("Response must not be blank")
        if expected_revision is not None and expected_revision < 1:
            raise ValueError("Revision must be positive")
        return await self.store.save_response(ticket_id, text, expected_revision, approve, adopted_generation_id, provenance_supplied)

    async def create(self, subject: str, description: str, key: str | None) -> tuple[TicketView, bool]:
        return await self.store.create_ticket(subject, description, key)

    async def get(self, ticket_id: UUID) -> TicketView | None:
        return await self.store.get_ticket(ticket_id)

    async def update_classification(self, ticket_id: UUID, expected_revision: int, changes: dict[str, list[UUID] | UUID]) -> TicketView:
        return await self.store.update_classification(ticket_id, expected_revision, changes)

    async def list(self, filters: TicketFilters) -> TicketPage:
        return await self.store.list_tickets(filters)

    async def retry(self, ticket_id: UUID) -> str:
        if await self.store.retry_classification(ticket_id):
            return "pending"
        return "missing" if await self.store.get_ticket(ticket_id) is None else "conflict"

    async def list_options(self) -> list[Option]:
        return await self.store.list_options()

    async def create_option(self, kind: str, name: str, color: str) -> Option:
        return await self.store.create_option(kind, name, color)

    async def update_option(self, option_id: UUID, changes: dict[str, object]) -> Option | None:
        return await self.store.update_option(option_id, changes)
