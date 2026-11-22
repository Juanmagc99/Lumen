"""Durable response jobs and coordinated provider-call reservations."""

from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import func, or_, select, text, update

from lumen.adapters.outbound.db.models import KnowledgeBase, ResponseAttempt, ResponseCallReservation, ResponseGeneration, Ticket
from lumen.adapters.outbound.db.session import DatabaseSessions
from lumen.adapters.outbound.db.tickets import storage_session


class PostgresResponseGenerations:
    def __init__(self, sessions: DatabaseSessions, settings):
        self._sessions, self._settings = sessions, settings

    async def request(self, ticket_id, base_id):
        async with storage_session(self._sessions) as session:
            await session.execute(text("SELECT pg_advisory_xact_lock(8139201)"))
            ticket = await session.get(Ticket, ticket_id)
            if ticket is None or (base_id is not None and await session.get(KnowledgeBase, base_id) is None):
                return "missing", None
            existing = await session.scalar(select(ResponseGeneration).where(ResponseGeneration.ticket_id == ticket_id, ResponseGeneration.status.in_(("queued", "running"))))
            if existing:
                return "existing", existing.id
            count = await session.scalar(select(func.count()).select_from(ResponseGeneration).where(ResponseGeneration.status.in_(("queued", "running"))))
            if count >= self._settings.queue_limit:
                return "full", None
            job = ResponseGeneration(ticket_id=ticket_id, knowledge_base_id=base_id, subject=ticket.subject, description=ticket.description)
            session.add(job)
            await session.commit()
            return "created", job.id

    async def list_for_ticket(self, ticket_id):
        async with storage_session(self._sessions) as session:
            if await session.get(Ticket, ticket_id) is None:
                return None
            jobs = (await session.scalars(select(ResponseGeneration).where(ResponseGeneration.ticket_id == ticket_id).order_by(ResponseGeneration.created_at.desc()))).all()
            result = []
            for job in jobs:
                attempts = (await session.scalars(select(ResponseAttempt).where(ResponseAttempt.generation_id == job.id).order_by(ResponseAttempt.started_at))).all()
                result.append({"id": job.id, "ticket_id": job.ticket_id, "knowledge_base_id": job.knowledge_base_id, "status": job.status, "created_at": job.created_at, "finished_at": job.finished_at, "original_text": job.original_text, "rationale": job.rationale, "insufficient_evidence": job.insufficient_evidence, "failure_reason": job.failure_reason, "attempts": [{"status": a.status, "started_at": a.started_at, "finished_at": a.finished_at, "requested_model": a.requested_model, "reported_model": a.reported_model, "provider": a.provider, "config_version": a.config_version, "sources": a.sources, "citations": a.citations, "provider_request_id": a.provider_request_id, "input_tokens": a.input_tokens, "output_tokens": a.output_tokens, "estimated_cost": a.estimated_cost, "currency": a.currency, "pricing_basis": a.pricing_basis, "failure_reason": a.failure_reason, "retrieval_mode": a.retrieval_mode, "retrieval_reason": a.retrieval_reason, "embedding_input_tokens": a.embedding_input_tokens} for a in attempts]})
            return result

    async def claim(self):
        async with storage_session(self._sessions) as session:
            now = await session.scalar(select(func.now()))
            job = await session.scalar(select(ResponseGeneration).where(or_((ResponseGeneration.status == "queued") & (ResponseGeneration.available_at <= now), (ResponseGeneration.status == "running") & (ResponseGeneration.claim_expires_at <= now))).order_by(ResponseGeneration.available_at, ResponseGeneration.created_at).with_for_update(skip_locked=True).limit(1))
            if job is None:
                return None
            if job.status == "running":
                await session.execute(update(ResponseAttempt).where(ResponseAttempt.generation_id == job.id, ResponseAttempt.claim_token == job.claim_token, ResponseAttempt.status == "running").values(status="unknown", finished_at=now, failure_reason="claim_expired"))
            if job.attempts >= self._settings.max_attempts:
                job.status, job.claim_token, job.claim_expires_at, job.finished_at, job.failure_reason = "failed", None, None, now, "attempts_exhausted"
                await session.commit()
                return None
            job.status, job.claim_token, job.claim_expires_at = "running", uuid4(), now + timedelta(seconds=self._settings.claim_seconds)
            claim = {"id": job.id, "token": job.claim_token, "subject": job.subject, "description": job.description, "knowledge_base_id": job.knowledge_base_id}
            await session.commit()
            return claim

    async def begin_attempt(self, claim, evidence, model_name, reserve_call, retrieval=None):
        async with storage_session(self._sessions) as session:
            await session.execute(text("SELECT pg_advisory_xact_lock(8139202)"))
            job = await session.scalar(select(ResponseGeneration).where(ResponseGeneration.id == claim["id"]).with_for_update())
            now = await session.scalar(select(func.now()))
            if job is None or job.status != "running" or job.claim_token != claim["token"] or job.claim_expires_at <= now:
                return None
            if reserve_call:
                active = await session.scalar(select(func.count()).select_from(ResponseCallReservation).where(ResponseCallReservation.released_at.is_(None), ResponseCallReservation.expires_at > now))
                recent = await session.scalar(select(func.count()).select_from(ResponseCallReservation).where(ResponseCallReservation.reserved_at > now - timedelta(seconds=self._settings.window_seconds)))
                if active >= self._settings.concurrency or recent >= self._settings.requests_per_window:
                    job.status, job.claim_token, job.claim_expires_at = "queued", None, None
                    job.available_at = now + timedelta(seconds=2)
                    await session.commit()
                    return None
            sources = [{"chunk_id": str(e.chunk_id), "version_id": str(e.version_id), "document_id": str(e.document_id), "document_name": e.document_name, "version": e.version, "excerpt": e.excerpt} for e in evidence]
            attempt = ResponseAttempt(generation_id=job.id, claim_token=claim["token"], status="running", requested_model=model_name, provider=model_name.split("/", 1)[0] if model_name and "/" in model_name else None, config_version="general-response-v1" if job.knowledge_base_id is None else "grounded-response-v1", sources=sources)
            if retrieval is not None:
                attempt.retrieval_mode, attempt.retrieval_reason, attempt.embedding_input_tokens = retrieval.mode, retrieval.reason, retrieval.input_tokens
            session.add(attempt)
            await session.flush()
            if reserve_call:
                session.add(ResponseCallReservation(attempt_id=attempt.id, expires_at=now + timedelta(seconds=self._settings.claim_seconds)))
            job.attempts += 1
            attempt_id = attempt.id
            await session.commit()
            return attempt_id

    async def finish(self, claim, attempt_id, result=None, failure=None):
        async with storage_session(self._sessions) as session:
            job = await session.scalar(select(ResponseGeneration).where(ResponseGeneration.id == claim["id"]).with_for_update())
            attempt = await session.get(ResponseAttempt, attempt_id, with_for_update=True)
            now = await session.scalar(select(func.now()))
            if job is None or attempt is None or job.status != "running" or job.claim_token != claim["token"] or job.claim_expires_at <= now:
                return False
            reservation = await session.scalar(select(ResponseCallReservation).where(ResponseCallReservation.attempt_id == attempt_id).with_for_update())
            if reservation:
                reservation.released_at = now
            attempt.finished_at = now
            if failure:
                attempt.status, attempt.failure_reason = "failed", failure
                job.failure_reason = failure
                job.status = "failed" if job.attempts >= self._settings.max_attempts else "queued"
                job.available_at = now + timedelta(seconds=self._settings.retry_seconds)
                job.finished_at = now if job.status == "failed" else None
            else:
                attempt.status, attempt.reported_model, attempt.provider_request_id = "completed", result.reported_model, result.request_id
                attempt.input_tokens, attempt.output_tokens = result.input_tokens, result.output_tokens
                if result.input_tokens is not None and result.output_tokens is not None and self._settings.input_price_per_million is not None and self._settings.output_price_per_million is not None:
                    attempt.estimated_cost = (Decimal(result.input_tokens) * self._settings.input_price_per_million + Decimal(result.output_tokens) * self._settings.output_price_per_million) / Decimal(1000000)
                    attempt.currency = self._settings.currency
                    attempt.pricing_basis = f"per million tokens: input {self._settings.input_price_per_million}, output {self._settings.output_price_per_million}"
                attempt.citations = [str(item) for item in result.citations]
                job.status, job.finished_at, job.failure_reason = "completed", now, None
                job.original_text, job.rationale, job.insufficient_evidence = result.text, result.rationale, result.insufficient_evidence
            job.claim_token, job.claim_expires_at = None, None
            await session.commit()
            return True
