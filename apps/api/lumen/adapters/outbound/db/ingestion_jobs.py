"""Claim and complete recoverable document ingestion jobs."""

from datetime import timedelta
from uuid import uuid4

from sqlalchemy import delete, func, or_, select

from lumen.adapters.outbound.db.models import IngestionJob, KnowledgeChunk, KnowledgeVersion
from lumen.adapters.outbound.db.session import DatabaseSessions
from lumen.adapters.outbound.db.tickets import storage_session


class PostgresIngestionJobs:
    def __init__(self, sessions: DatabaseSessions, max_attempts: int = 3, claim_seconds: int = 120):
        self._sessions = sessions
        self._max_attempts = max_attempts
        self._claim_seconds = claim_seconds

    async def claim(self):
        async with storage_session(self._sessions) as session:
            now = await session.scalar(select(func.now()))
            job = await session.scalar(select(IngestionJob).where(or_(
                (IngestionJob.status == "pending") & (IngestionJob.available_at <= now),
                (IngestionJob.status == "processing") & (IngestionJob.claim_expires_at <= now),
            )).order_by(IngestionJob.available_at, IngestionJob.version_id).with_for_update(skip_locked=True).limit(1))
            if job is None:
                return None
            if job.attempts >= self._max_attempts:
                job.status, job.claim_token, job.claim_expires_at = "failed", None, None
                job.failure_reason = "ATTEMPTS_EXHAUSTED"
                await session.commit()
                return None
            job.status, job.claim_token, job.claim_expires_at = "processing", uuid4(), now + timedelta(seconds=self._claim_seconds)
            job.attempts += 1
            version = await session.get(KnowledgeVersion, job.version_id)
            claim = (job.version_id, job.claim_token, version.content)
            await session.commit()
            return claim

    async def finish(self, claim, chunks: list[str] | None):
        version_id, token, _ = claim
        async with storage_session(self._sessions) as session:
            job = await session.scalar(select(IngestionJob).where(IngestionJob.version_id == version_id).with_for_update())
            now = await session.scalar(select(func.now()))
            if job is None or job.status != "processing" or job.claim_token != token or job.claim_expires_at <= now:
                return False
            if chunks is None:
                job.status = "failed" if job.attempts >= self._max_attempts else "pending"
                job.available_at = now + timedelta(seconds=10)
                job.failure_reason = "INGESTION_FAILED"
            else:
                await session.execute(delete(KnowledgeChunk).where(KnowledgeChunk.version_id == version_id))
                session.add_all([KnowledgeChunk(version_id=version_id, position=index, content=part) for index, part in enumerate(chunks)])
                job.status, job.failure_reason = "ready", None
            job.claim_token, job.claim_expires_at = None, None
            await session.commit()
            return True
