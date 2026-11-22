"""HTTP routes and translation of application results."""

from datetime import date
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, Response

from lumen.adapters.inbound.http.options import OptionCreate, OptionUpdate, OptionView
from lumen.adapters.inbound.http.schemas import ClassificationWrite, ResponseView, ResponseWrite, TicketCreate, TicketDetail, TicketPage
from lumen.application.tickets import Tickets
from lumen.domain.tickets import ClassificationConflict, DuplicateOption, InvalidClassificationOption, KeyConflict, StorageUnavailable, TicketFilters
from lumen.domain.responses import InvalidGeneration, ResponseConflict, TicketMissing

ClassificationStatus = Literal["pending", "processing", "completed", "failed", "unavailable"]


def router_for(tickets: Tickets) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/api/classification-options", response_model=list[OptionView])
    async def read_options():
        try:
            return await tickets.list_options()
        except StorageUnavailable:
            raise HTTPException(status_code=503, detail="Option storage is unavailable. Try again later.") from None

    @router.post("/api/classification-options", response_model=OptionView, status_code=201)
    async def create_option(data: OptionCreate):
        try:
            return await tickets.create_option(data.kind, data.name, data.color)
        except DuplicateOption:
            raise HTTPException(status_code=409, detail="An option with this name already exists for this type.") from None
        except StorageUnavailable:
            raise HTTPException(status_code=503, detail="Option storage is unavailable. Try again later.") from None

    @router.patch("/api/classification-options/{option_id}", response_model=OptionView)
    async def update_option(option_id: UUID, data: OptionUpdate):
        changes = data.model_dump(exclude_unset=True)
        if not changes or any(value is None for value in changes.values()):
            raise HTTPException(status_code=422, detail="Provide a name, color, or active state.")
        try:
            option = await tickets.update_option(option_id, changes)
            if option is None:
                raise HTTPException(status_code=404, detail="Option not found.")
            return option
        except DuplicateOption:
            raise HTTPException(status_code=409, detail="An option with this name already exists for this type.") from None
        except StorageUnavailable:
            raise HTTPException(status_code=503, detail="Option storage is unavailable. Try again later.") from None

    @router.post("/api/tickets", response_model=TicketDetail, status_code=201)
    async def post_ticket(data: TicketCreate, response: Response, idempotency_key: Annotated[str | None, Header(min_length=1, max_length=255, pattern=r"^[\x21-\x7e]+$")] = None):
        try:
            ticket, created = await tickets.create(data.subject, data.description, idempotency_key)
            response.status_code = 201 if created else 200
            return ticket
        except KeyConflict:
            raise HTTPException(status_code=409, detail="Idempotency key was already used with different content.") from None
        except StorageUnavailable:
            raise HTTPException(status_code=503, detail="Ticket storage is unavailable. Try again later.") from None

    @router.get("/api/tickets", response_model=TicketPage)
    async def read_tickets(q: str | None = None, status: ClassificationStatus | None = None, date_from: date | None = None, date_to: date | None = None, page: Annotated[int, Query(ge=1)] = 1, page_size: Annotated[int, Query(ge=1, le=100)] = 25, category_id: UUID | None = None, priority_id: UUID | None = None, statuses: Annotated[list[ClassificationStatus] | None, Query()] = None, category_ids: Annotated[list[UUID] | None, Query()] = None, priority_ids: Annotated[list[UUID] | None, Query()] = None):
        if date_from and date_to and date_from > date_to:
            raise HTTPException(status_code=422, detail="Start date must not be after end date.")
        try:
            return await tickets.list(TicketFilters(q, status, date_from, date_to, page, page_size, category_id, priority_id, tuple(dict.fromkeys(statuses or [])), tuple(dict.fromkeys(category_ids or [])), tuple(dict.fromkeys(priority_ids or []))))
        except StorageUnavailable:
            raise HTTPException(status_code=503, detail="Ticket storage is unavailable. Try again later.") from None

    @router.get("/api/tickets/{ticket_id}", response_model=TicketDetail)
    async def read_ticket(ticket_id: UUID):
        try:
            ticket = await tickets.get(ticket_id)
            if ticket is None:
                raise HTTPException(status_code=404, detail="Ticket not found.")
            return ticket
        except StorageUnavailable:
            raise HTTPException(status_code=503, detail="Ticket storage is unavailable. Try again later.") from None

    @router.post("/api/tickets/{ticket_id}/classification/retry", status_code=202)
    async def retry_classification(ticket_id: UUID):
        try:
            result = await tickets.retry(ticket_id)
            if result == "pending":
                return {"status": "pending"}
            if result == "missing":
                raise HTTPException(status_code=404, detail="Ticket not found.")
            raise HTTPException(status_code=409, detail="Classification is not in a failed state.")
        except StorageUnavailable:
            raise HTTPException(status_code=503, detail="Ticket storage is unavailable. Try again later.") from None

    @router.patch("/api/tickets/{ticket_id}/classification", response_model=TicketDetail)
    async def update_classification(ticket_id: UUID, data: ClassificationWrite):
        submitted = data.model_dump(exclude_unset=True, exclude={"expected_revision"})
        if not submitted or any(value is None for value in submitted.values()):
            raise HTTPException(status_code=422, detail="Select at least one category or priority.")
        changes = submitted
        try:
            return await tickets.update_classification(ticket_id, data.expected_revision, changes)
        except TicketMissing:
            raise HTTPException(status_code=404, detail="Ticket not found.") from None
        except ClassificationConflict:
            raise HTTPException(status_code=409, detail="Classification changed. Reload before trying again.") from None
        except InvalidClassificationOption:
            raise HTTPException(status_code=422, detail="Select an active option of the correct type.") from None
        except StorageUnavailable:
            raise HTTPException(status_code=503, detail="Ticket storage is unavailable. Try again later.") from None

    @router.get("/api/tickets/{ticket_id}/response", response_model=ResponseView | None)
    async def read_response(ticket_id: UUID):
        try:
            return await tickets.get_response(ticket_id)
        except TicketMissing:
            raise HTTPException(status_code=404, detail="Ticket not found.") from None
        except StorageUnavailable:
            raise HTTPException(status_code=503, detail="Response storage is unavailable. Try again later.") from None

    async def write_response(ticket_id: UUID, data: ResponseWrite, approve: bool):
        try:
            return await tickets.save_response(ticket_id, data.text, data.expected_revision, approve, data.adopted_generation_id, "adopted_generation_id" in data.model_fields_set)
        except TicketMissing:
            raise HTTPException(status_code=404, detail="Ticket not found.") from None
        except ResponseConflict:
            raise HTTPException(status_code=409, detail="Response changed. Reload the saved version before trying again.") from None
        except InvalidGeneration:
            raise HTTPException(status_code=422, detail="Select a completed generation for this ticket.") from None
        except StorageUnavailable:
            raise HTTPException(status_code=503, detail="Response storage is unavailable. Try again later.") from None

    @router.put("/api/tickets/{ticket_id}/response", response_model=ResponseView)
    async def save_response(ticket_id: UUID, data: ResponseWrite):
        return await write_response(ticket_id, data, False)

    @router.post("/api/tickets/{ticket_id}/response/approval", response_model=ResponseView)
    async def approve_response(ticket_id: UUID, data: ResponseWrite):
        return await write_response(ticket_id, data, True)

    return router
