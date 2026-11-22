"""Durable PostgreSQL classification claims and completion."""

import uuid

from sqlalchemy import and_, func, or_, select

from lumen.adapters.outbound.db.session import DatabaseSessions
from lumen.adapters.outbound.db.models import ClassificationJob, ClassificationOption, Ticket
from lumen.domain.classification import ClaimedClassification, ClassificationDecision, ClassificationOption as OptionValue, ClassificationPolicy


class PostgresClassificationJobs:
    def __init__(self, policy: ClassificationPolicy, sessions: DatabaseSessions):
        self.policy = policy
        self._sessions = sessions

    async def claim(self) -> ClaimedClassification | None:
        async with self._sessions.scope() as session:
            now = await session.scalar(select(func.clock_timestamp()))
            job = await session.scalar(
                select(ClassificationJob)
                .where(or_(
                    and_(ClassificationJob.status == "pending", ClassificationJob.available_at <= now),
                    and_(ClassificationJob.status == "processing", ClassificationJob.claim_expires_at <= now),
                ))
                .order_by(ClassificationJob.available_at, ClassificationJob.ticket_id)
                .with_for_update(skip_locked=True)
                .limit(1)
            )
            if job is None:
                return None
            if self.policy.exhausted(job.attempts):
                job.status = "failed"
                job.claim_token = None
                job.claim_expires_at = None
                await session.commit()
                return None
            job.status = "processing"
            job.attempts += 1
            job.claim_token = uuid.uuid4()
            job.claim_expires_at = self.policy.claim_expires_at(now)
            ticket = await session.get(Ticket, job.ticket_id)
            claim = ClaimedClassification(job.ticket_id, job.claim_token, ticket.subject, ticket.description)
            await session.commit()
            return claim

    async def active_options(self) -> list[OptionValue]:
        async with self._sessions.scope() as session:
            options = await session.scalars(select(ClassificationOption).where(ClassificationOption.active.is_(True)))
            return [OptionValue(option.id, option.name, option.kind) for option in options]

    async def finish(self, claim: ClaimedClassification, decision: ClassificationDecision | None = None, failure_reason: str | None = None) -> None:
        async with self._sessions.scope() as session:
            job = await session.scalar(select(ClassificationJob).where(ClassificationJob.ticket_id == claim.ticket_id).with_for_update())
            if job is None or job.status != "processing" or job.claim_token != claim.token:
                return
            now = await session.scalar(select(func.clock_timestamp()))
            if job.claim_expires_at <= now:
                return
            if decision is not None:
                active = list(await session.scalars(select(ClassificationOption).where(ClassificationOption.active.is_(True)).order_by(ClassificationOption.id).with_for_update()))
                now = await session.scalar(select(func.clock_timestamp()))
                if job.claim_expires_at <= now:
                    return
                valid = {option.id: option.kind for option in active if option.active}
                if not {"category", "priority"}.issubset(set(valid.values())):
                    decision = None
                    failure_reason = "no_options"
                elif len(decision.category_ids) != len(set(decision.category_ids)) or any(valid.get(category_id) != "category" for category_id in decision.category_ids) or (decision.priority_id is not None and valid.get(decision.priority_id) != "priority"):
                    decision = None
                    failure_reason = "invalid_decision"
            if decision is not None:
                job.status = "completed"
                job.result = None
                job.result_source = "model"
                selected = set(decision.category_ids)
                job.categories = [option for option in active if option.id in selected]
                job.priority_id = decision.priority_id
                job.failure_reason = None
            else:
                job.failure_reason = failure_reason or "provider"
                if self.policy.exhausted(job.attempts):
                    job.status = "failed"
                else:
                    job.status = "pending"
                    job.available_at = self.policy.retry_at(now)
            job.claim_token = None
            job.claim_expires_at = None
            await session.commit()
