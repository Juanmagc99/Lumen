"""Durable semantic indexing of the latest active knowledge versions."""

from uuid import uuid4

from sqlalchemy import text

from lumen.adapters.outbound.db.tickets import storage_session


class PostgresSemanticIndex:
    def __init__(self, sessions):
        self._sessions = sessions

    async def claim(self, settings):
        params = {"model": settings.model, "dimensions": settings.dimensions}
        async with storage_session(self._sessions) as session:
            await session.execute(text("""
                INSERT INTO semantic_index_jobs(version_id, model, dimensions)
                SELECT v.id, :model, :dimensions FROM knowledge_versions v
                JOIN knowledge_documents d ON d.id = v.document_id AND d.active
                JOIN ingestion_jobs i ON i.version_id = v.id AND i.status = 'ready'
                WHERE NOT EXISTS (SELECT 1 FROM knowledge_versions n JOIN ingestion_jobs ni
                    ON ni.version_id = n.id AND ni.status = 'ready'
                    WHERE n.document_id = d.id AND n.version > v.version)
                ON CONFLICT DO NOTHING
            """), params)
            row = (await session.execute(text("""
                SELECT j.version_id, j.attempts FROM semantic_index_jobs j
                JOIN knowledge_versions v ON v.id = j.version_id
                JOIN knowledge_documents d ON d.id = v.document_id AND d.active
                JOIN ingestion_jobs i ON i.version_id = v.id AND i.status = 'ready'
                WHERE j.model = :model AND j.dimensions = :dimensions
                  AND ((j.status = 'pending' AND j.available_at <= now()) OR
                       (j.status = 'processing' AND j.claim_expires_at <= now()))
                  AND NOT EXISTS (SELECT 1 FROM knowledge_versions n JOIN ingestion_jobs ni
                    ON ni.version_id = n.id AND ni.status = 'ready'
                    WHERE n.document_id = d.id AND n.version > v.version)
                ORDER BY j.available_at, j.version_id FOR UPDATE OF j SKIP LOCKED LIMIT 1
            """), params)).mappings().first()
            if row is None:
                await session.commit()
                return None
            params.update(version_id=row["version_id"], token=uuid4())
            if row["attempts"] >= 3:
                await session.execute(text("""UPDATE semantic_index_jobs SET status='failed', claim_token=NULL,
                    claim_expires_at=NULL, failure_reason='Indexing attempts exhausted.'
                    WHERE version_id=:version_id AND model=:model AND dimensions=:dimensions"""), params)
                await session.commit()
                return None
            await session.execute(text("""UPDATE semantic_index_jobs SET status='processing', attempts=attempts+1,
                claim_token=:token, claim_expires_at=now()+interval '180 seconds'
                WHERE version_id=:version_id AND model=:model AND dimensions=:dimensions"""), params)
            chunks = (await session.execute(text("SELECT id, content FROM knowledge_chunks WHERE version_id=:version_id ORDER BY position"), params)).all()
            await session.commit()
            return params, chunks

    async def renew(self, claim):
        async with storage_session(self._sessions) as session:
            result = await session.execute(text("""UPDATE semantic_index_jobs SET claim_expires_at=now()+interval '180 seconds'
                WHERE version_id=:version_id AND model=:model AND dimensions=:dimensions AND status='processing'
                AND claim_token=:token AND claim_expires_at > now()"""), claim)
            await session.commit()
            return result.rowcount == 1

    async def finish(self, claim, vectors, tokens, failure=None):
        async with storage_session(self._sessions) as session:
            row = (await session.execute(text("""SELECT j.attempts, d.active,
                    NOT EXISTS (SELECT 1 FROM knowledge_versions n JOIN ingestion_jobs ni
                        ON ni.version_id=n.id AND ni.status='ready'
                        WHERE n.document_id=d.id AND n.version>v.version) AS current
                FROM semantic_index_jobs j JOIN knowledge_versions v ON v.id=j.version_id
                JOIN knowledge_documents d ON d.id=v.document_id
                WHERE j.version_id=:version_id AND j.model=:model AND j.dimensions=:dimensions
                  AND j.status='processing' AND j.claim_token=:token AND j.claim_expires_at>now()
                FOR UPDATE OF j, d"""), claim)).mappings().first()
            if row is None:
                return False
            if failure or not row["active"] or not row["current"]:
                params = dict(claim, status="failed" if row["attempts"] >= 3 else "pending", reason="Semantic indexing unavailable.")
                await session.execute(text("""UPDATE semantic_index_jobs SET status=:status, failure_reason=:reason,
                    available_at=now()+interval '10 seconds', claim_token=NULL, claim_expires_at=NULL
                    WHERE version_id=:version_id AND model=:model AND dimensions=:dimensions"""), params)
            else:
                for chunk_id, vector in vectors:
                    await session.execute(text("""INSERT INTO knowledge_embeddings(chunk_id, model, dimensions, embedding)
                        VALUES (:chunk, :model, :dimensions, CAST(:vector AS vector))
                        ON CONFLICT (chunk_id,model,dimensions) DO UPDATE SET embedding=EXCLUDED.embedding"""),
                        dict(claim, chunk=chunk_id, vector="[" + ",".join(map(str, vector)) + "]"))
                await session.execute(text("""UPDATE semantic_index_jobs SET status='ready', failure_reason=NULL,
                    input_tokens=:tokens, claim_token=NULL, claim_expires_at=NULL
                    WHERE version_id=:version_id AND model=:model AND dimensions=:dimensions"""), dict(claim, tokens=tokens))
            await session.commit()
            return True
