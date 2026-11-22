"""PostgreSQL knowledge persistence."""

from uuid import UUID

from sqlalchemy import func, select, text

from lumen.adapters.outbound.db.models import IngestionJob, KnowledgeBase, KnowledgeDocument, KnowledgeVersion
from lumen.adapters.outbound.db.tickets import storage_session
from lumen.adapters.outbound.db.session import DatabaseSessions
from lumen.domain.errors import failure_message


class PostgresKnowledge:
    def __init__(self, sessions: DatabaseSessions, embedding_config=None):
        self._sessions = sessions
        self._embedding_config = embedding_config or (lambda: ("text-embedding-3-small", 1536))

    async def list_bases(self):
        async with storage_session(self._sessions) as session:
            return [{"id": b.id, "name": b.name, "created_at": b.created_at} for b in (await session.scalars(select(KnowledgeBase).order_by(KnowledgeBase.name, KnowledgeBase.id))).all()]

    async def create_base(self, name: str):
        async with storage_session(self._sessions) as session:
            base = KnowledgeBase(name=name)
            session.add(base)
            await session.commit()
            await session.refresh(base)
            return {"id": base.id, "name": base.name, "created_at": base.created_at}

    async def list_documents(self, base_id: UUID):
        async with storage_session(self._sessions) as session:
            if await session.get(KnowledgeBase, base_id) is None:
                return None
            rows = (await session.execute(select(KnowledgeDocument, KnowledgeVersion, IngestionJob).join(KnowledgeVersion, KnowledgeVersion.document_id == KnowledgeDocument.id).join(IngestionJob, IngestionJob.version_id == KnowledgeVersion.id).where(KnowledgeDocument.knowledge_base_id == base_id).order_by(KnowledgeDocument.created_at, KnowledgeVersion.version.desc()))).all()
            model, dimensions = self._embedding_config()
            index_rows = (await session.execute(text("""SELECT version_id, status, failure_reason FROM semantic_index_jobs
                WHERE model=:model AND dimensions=:dimensions AND version_id IN
                (SELECT v.id FROM knowledge_versions v JOIN knowledge_documents d ON d.id=v.document_id WHERE d.knowledge_base_id=:base_id)"""),
                {"model": model, "dimensions": dimensions, "base_id": base_id})).mappings().all()
            indexes = {item["version_id"]: item for item in index_rows}
            latest_ready = {}
            for document, version, job in rows:
                if job.status == "ready" and document.id not in latest_ready:
                    latest_ready[document.id] = version.id
            return [{"id": d.id, "name": d.name, "active": d.active, "version_id": v.id, "version": v.version, "status": j.status, "failure_reason": failure_message("ingestion", j.failure_reason),
                     "semantic_status": (indexes[v.id]["status"] if v.id in indexes else "pending") if d.active and latest_ready.get(d.id) == v.id else None,
                     "semantic_failure_reason": failure_message("indexing", indexes[v.id]["failure_reason"]) if v.id in indexes else None} for d, v, j in rows]

    async def create_document(self, base_id: UUID, name: str, content: str):
        async with storage_session(self._sessions) as session:
            if await session.get(KnowledgeBase, base_id) is None:
                return None
            document = KnowledgeDocument(knowledge_base_id=base_id, name=name)
            session.add(document)
            await session.flush()
            version = KnowledgeVersion(document_id=document.id, version=1, content=content)
            session.add(version)
            await session.flush()
            session.add(IngestionJob(version_id=version.id))
            await session.commit()
            return {"document_id": document.id, "version_id": version.id, "version": 1, "status": "pending"}

    async def add_version(self, document_id: UUID, content: str):
        async with storage_session(self._sessions) as session:
            document = await session.scalar(select(KnowledgeDocument).where(KnowledgeDocument.id == document_id).with_for_update())
            if document is None:
                return None
            number = (await session.scalar(select(func.max(KnowledgeVersion.version)).where(KnowledgeVersion.document_id == document_id)) or 0) + 1
            version = KnowledgeVersion(document_id=document_id, version=number, content=content)
            session.add(version)
            await session.flush()
            session.add(IngestionJob(version_id=version.id))
            await session.commit()
            return {"document_id": document_id, "version_id": version.id, "version": number, "status": "pending"}

    async def set_active(self, document_id: UUID, active: bool):
        async with storage_session(self._sessions) as session:
            document = await session.get(KnowledgeDocument, document_id, with_for_update=True)
            if document is None:
                return None
            document.active = active
            await session.commit()
            return {"id": document.id, "active": document.active}

    async def get_version(self, version_id: UUID):
        async with storage_session(self._sessions) as session:
            row = (await session.execute(select(KnowledgeDocument, KnowledgeVersion, IngestionJob).join(KnowledgeVersion, KnowledgeVersion.document_id == KnowledgeDocument.id).join(IngestionJob, IngestionJob.version_id == KnowledgeVersion.id).where(KnowledgeVersion.id == version_id))).one_or_none()
            if row is None:
                return None
            d, v, j = row
            return {"document_id": d.id, "name": d.name, "version_id": v.id, "version": v.version, "content": v.content, "status": j.status, "failure_reason": failure_message("ingestion", j.failure_reason)}

    async def retry(self, version_id: UUID):
        async with storage_session(self._sessions) as session:
            job = await session.get(IngestionJob, version_id, with_for_update=True)
            if job is None:
                return "missing"
            if job.status != "failed":
                return "conflict"
            job.status, job.attempts, job.failure_reason, job.available_at = "pending", 0, None, func.now()
            await session.commit()
            return "pending"

    async def retry_semantic(self, version_id: UUID):
        model, dimensions = self._embedding_config()
        async with storage_session(self._sessions) as session:
            result = await session.execute(text("""UPDATE semantic_index_jobs SET status='pending', attempts=0,
                failure_reason=NULL, available_at=now() WHERE version_id=:version_id AND model=:model
                AND dimensions=:dimensions AND status='failed'"""),
                {"version_id": version_id, "model": model, "dimensions": dimensions})
            await session.commit()
            return "pending" if result.rowcount else "conflict"
