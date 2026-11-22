"""PostgreSQL ticket and classification-option operations."""

from contextlib import asynccontextmanager
from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from lumen.adapters.outbound.db.models import ClassificationJob, ClassificationOption, IdempotencyKey, ResponseGeneration, Ticket, TicketResponse, classification_job_categories, ticket_manual_categories
from lumen.adapters.outbound.db.session import DatabaseSessions
from lumen.domain.tickets import ClassificationConflict, DuplicateOption, InvalidClassificationOption, KeyConflict, Option, StorageUnavailable, TicketFilters, TicketPage, TicketView
from lumen.domain.responses import InvalidGeneration, ResponseConflict, ResponseView, TicketMissing
from lumen.domain.errors import failure_code


@asynccontextmanager
async def storage_session(sessions: DatabaseSessions):
    try:
        async with sessions.scope() as session:
            yield session
    except (SQLAlchemyError, OSError, RuntimeError):
        raise StorageUnavailable from None


def option_value(option: ClassificationOption | None) -> Option | None:
    return Option(option.id, option.kind, option.name, option.active, option.color) if option is not None else None


async def response_value(session, response: TicketResponse) -> ResponseView:
    generation = await session.get(ResponseGeneration, response.adopted_generation_id) if response.adopted_generation_id else None
    provenance = "manual" if generation is None else "ai" if response.text == generation.original_text else "ai_edited"
    return ResponseView(response.ticket_id, response.text, response.status, response.edited_at, response.revision, response.adopted_generation_id, provenance)


def ticket_value(ticket: Ticket) -> TicketView:
    categories = ticket.manual_categories if ticket.manual_categories_override else ticket.classification_categories
    priority = ticket.manual_priority or ticket.classification_priority
    return TicketView(
        id=ticket.id,
        subject=ticket.subject,
        description=ticket.description,
        received_at=ticket.received_at,
        classification_status=ticket.classification_status,
        classification_result=ticket.classification_result,
        classification_source=ticket.classification_source,
        classification_categories=[option_value(option) for option in ticket.classification_categories],
        classification_priority=option_value(ticket.classification_priority),
        classification_failure_reason=failure_code("classification", ticket.classification_failure_reason),
        effective_categories=[option_value(option) for option in categories],
        effective_priority=option_value(priority),
        category_origin="manual" if ticket.manual_categories_override else ticket.classification_source,
        priority_origin=("manual" if ticket.manual_priority_id else ticket.classification_source) if priority else None,
        classification_revision=ticket.classification_revision,
    )


class PostgresTickets:
    def __init__(self, sessions: DatabaseSessions):
        self._sessions = sessions

    async def get_response(self, ticket_id: UUID) -> ResponseView | None:
        async with storage_session(self._sessions) as session:
            if await session.get(Ticket, ticket_id) is None:
                raise TicketMissing
            response = await session.get(TicketResponse, ticket_id)
            return await response_value(session, response) if response else None

    async def save_response(self, ticket_id: UUID, text: str, expected_revision: int | None, approve: bool, adopted_generation_id: UUID | None, provenance_supplied: bool) -> ResponseView:
        async with storage_session(self._sessions) as session:
            # Serialize creation and updates even when no response row exists yet.
            if await session.scalar(select(Ticket.id).where(Ticket.id == ticket_id).with_for_update()) is None:
                raise TicketMissing
            response = await session.get(TicketResponse, ticket_id)
            if (response is None and expected_revision is not None) or (response is not None and response.revision != expected_revision):
                raise ResponseConflict
            if provenance_supplied and adopted_generation_id is not None:
                generation = await session.get(ResponseGeneration, adopted_generation_id)
                if generation is None or generation.ticket_id != ticket_id or generation.status != "completed" or generation.original_text is None:
                    raise InvalidGeneration
            if response is None:
                response = TicketResponse(ticket_id=ticket_id, text=text, status="approved" if approve else "draft", revision=1, adopted_generation_id=adopted_generation_id if provenance_supplied else None)
                session.add(response)
            else:
                changed = response.text != text
                if changed:
                    response.text = text
                    response.edited_at = func.now()
                if approve:
                    response.status = "approved"
                elif changed:
                    response.status = "draft"
                response.revision += 1
                if provenance_supplied:
                    response.adopted_generation_id = adopted_generation_id
            await session.commit()
            await session.refresh(response)
            return await response_value(session, response)

    async def create_ticket(self, subject: str, description: str, key: str | None) -> tuple[TicketView, bool]:
        async with storage_session(self._sessions) as session:
            ticket = Ticket(subject=subject, description=description)
            session.add(ticket)
            try:
                await session.flush()
                session.add(ClassificationJob(ticket_id=ticket.id))
                if key is not None:
                    session.add(IdempotencyKey(key=key, ticket_id=ticket.id))
                await session.commit()
            except IntegrityError:
                await session.rollback()
                if key is None:
                    raise
                existing = await session.scalar(select(Ticket).join(IdempotencyKey, IdempotencyKey.ticket_id == Ticket.id).where(IdempotencyKey.key == key))
                if existing is None:
                    raise
                if existing.subject != subject or existing.description != description:
                    raise KeyConflict
                return ticket_value(existing), False
            await session.refresh(ticket, attribute_names=["received_at", "classification", "manual_categories", "manual_categories_override", "manual_priority", "classification_revision"])
            return ticket_value(ticket), True

    async def get_ticket(self, ticket_id: UUID) -> TicketView | None:
        async with storage_session(self._sessions) as session:
            ticket = await session.get(Ticket, ticket_id)
            return ticket_value(ticket) if ticket is not None else None

    async def update_classification(self, ticket_id: UUID, expected_revision: int, changes: dict[str, list[UUID] | UUID]) -> TicketView:
        async with storage_session(self._sessions) as session:
            ticket = await session.scalar(select(Ticket).where(Ticket.id == ticket_id).with_for_update(of=Ticket))
            if ticket is None:
                raise TicketMissing
            if ticket.classification_revision != expected_revision:
                raise ClassificationConflict
            categories = changes.get("category_ids")
            priority = changes.get("priority_id")
            if categories is not None and (not isinstance(categories, list) or len(categories) != len(set(categories))):
                raise InvalidClassificationOption
            requested = [("category", value) for value in (categories or [])]
            if priority is not None:
                requested.append(("priority", priority))
            retained = {option.id for option in (ticket.manual_categories if ticket.manual_categories_override else ticket.classification_categories)}
            selected = {}
            # Match the worker's option lock order to avoid lock-order deadlocks.
            for kind, option_id in sorted(requested, key=lambda item: item[1]):
                option = await session.scalar(select(ClassificationOption).where(ClassificationOption.id == option_id).with_for_update())
                if option is None or option.kind != kind or (not option.active and not (kind == "category" and option_id in retained)):
                    raise InvalidClassificationOption
                selected[option_id] = option
            if categories is not None:
                ticket.manual_categories = [selected[option_id] for option_id in categories]
                ticket.manual_categories_override = True
            if priority is not None:
                ticket.manual_priority = selected[priority]
            ticket.classification_revision += 1
            await session.commit()
            return ticket_value(ticket)

    async def list_tickets(self, filters: TicketFilters) -> TicketPage:
        predicates = []
        if filters.q and filters.q.strip():
            escaped = filters.q.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            predicates.append(Ticket.subject.ilike(f"%{escaped}%", escape="\\"))
        statuses = set(filters.statuses) | ({filters.status} if filters.status else set())
        category_ids = set(filters.category_ids) | ({filters.category_id} if filters.category_id else set())
        priority_ids = set(filters.priority_ids) | ({filters.priority_id} if filters.priority_id else set())
        if statuses:
            status_predicates = [ClassificationJob.status.in_(statuses - {"unavailable"})] if statuses - {"unavailable"} else []
            if "unavailable" in statuses:
                status_predicates.append(ClassificationJob.ticket_id.is_(None))
            predicates.append(or_(*status_predicates))
        if category_ids:
            manual_match = select(ticket_manual_categories.c.ticket_id).where(ticket_manual_categories.c.ticket_id == Ticket.id, ticket_manual_categories.c.category_id.in_(category_ids)).exists()
            model_match = select(classification_job_categories.c.ticket_id).where(classification_job_categories.c.ticket_id == Ticket.id, classification_job_categories.c.category_id.in_(category_ids)).exists()
            predicates.append(or_(and_(Ticket.manual_categories_override.is_(True), manual_match), and_(Ticket.manual_categories_override.is_(False), model_match)))
        if priority_ids:
            predicates.append(func.coalesce(Ticket.manual_priority_id, ClassificationJob.priority_id).in_(priority_ids))
        if filters.date_from:
            predicates.append(Ticket.received_at >= datetime.combine(filters.date_from, time.min, timezone.utc))
        if filters.date_to and filters.date_to < date.max:
            predicates.append(Ticket.received_at < datetime.combine(filters.date_to + timedelta(days=1), time.min, timezone.utc))
        async with storage_session(self._sessions) as session:
            base = select(Ticket).outerjoin(ClassificationJob).where(*predicates)
            total = await session.scalar(select(func.count()).select_from(Ticket).outerjoin(ClassificationJob).where(*predicates))
            result = await session.scalars(base.order_by(Ticket.received_at.desc(), Ticket.id.desc()).limit(filters.page_size).offset((filters.page - 1) * filters.page_size))
            return TicketPage([ticket_value(ticket) for ticket in result], filters.page, filters.page_size, total or 0)

    async def retry_classification(self, ticket_id: UUID) -> bool:
        async with storage_session(self._sessions) as session:
            result = await session.execute(update(ClassificationJob).where(ClassificationJob.ticket_id == ticket_id, ClassificationJob.status == "failed").values(status="pending", attempts=0, available_at=func.now(), claim_token=None, claim_expires_at=None, failure_reason=None))
            await session.commit()
            return result.rowcount == 1

    async def list_options(self) -> list[Option]:
        async with storage_session(self._sessions) as session:
            result = await session.scalars(select(ClassificationOption).order_by(ClassificationOption.kind, ClassificationOption.name, ClassificationOption.id))
            return [option_value(option) for option in result]

    async def create_option(self, kind: str, name: str, color: str) -> Option:
        async with storage_session(self._sessions) as session:
            option = ClassificationOption(kind=kind, name=name, active=True, color=color)
            session.add(option)
            try:
                await session.commit()
            except IntegrityError:
                raise DuplicateOption from None
            return option_value(option)

    async def update_option(self, option_id: UUID, changes: dict[str, object]) -> Option | None:
        async with storage_session(self._sessions) as session:
            option = await session.get(ClassificationOption, option_id)
            if option is None:
                return None
            for key, value in changes.items():
                setattr(option, key, value)
            try:
                await session.commit()
            except IntegrityError:
                raise DuplicateOption from None
            return option_value(option)
