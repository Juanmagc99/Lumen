"""Lexical retrieval restricted to active, ready knowledge versions."""

import re
from uuid import UUID

from sqlalchemy import text

from lumen.adapters.outbound.db.session import DatabaseSessions
from lumen.adapters.outbound.db.tickets import storage_session
from lumen.application.embeddings import EmbeddingFailure
from lumen.application.retrieval import Evidence, RetrievalResult
from lumen.domain.tickets import StorageUnavailable


class PostgresRetriever:
    def __init__(self, sessions: DatabaseSessions, embeddings=None, settings=None):
        self._sessions = sessions
        self._embeddings = embeddings
        self._settings = settings

    async def retrieve(self, base_id: UUID, query: str, limit: int = 8) -> RetrievalResult:
        try:
            return await self._retrieve(base_id, query, limit)
        except StorageUnavailable:
            return await self._retrieve(base_id, query, limit, lexical_only=True)

    async def _retrieve(self, base_id: UUID, query: str, limit: int, lexical_only: bool = False) -> RetrievalResult:
        words = list(dict.fromkeys(re.findall(r"[^\W_]+", query.lower(), re.UNICODE)))[:32]
        vector = None
        tokens = None
        reason = "semantic_unavailable"
        try:
            if lexical_only:
                raise EmbeddingFailure("semantic_unavailable")
            settings = self._settings()
            batch = await self._embeddings.embed([query[:20000]])
            vector, tokens = batch.vectors[0], batch.input_tokens
        except (EmbeddingFailure, RuntimeError, ValueError, TypeError):
            pass
        limit = min(max(limit, 1), 20)
        async with storage_session(self._sessions) as session:
            await session.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
            rows = (await session.execute(text("""
                WITH search AS (SELECT to_tsquery('simple', :query) AS q)
                SELECT c.id AS chunk_id, v.id AS version_id, d.id AS document_id,
                       d.name AS document_name, v.version, c.content AS excerpt
                FROM knowledge_documents d
                JOIN knowledge_versions v ON v.document_id = d.id
                JOIN ingestion_jobs j ON j.version_id = v.id AND j.status = 'ready'
                JOIN knowledge_chunks c ON c.version_id = v.id CROSS JOIN search
                WHERE d.knowledge_base_id = :base_id AND d.active
                  AND NOT EXISTS (
                    SELECT 1 FROM knowledge_versions newer
                    JOIN ingestion_jobs nj ON nj.version_id = newer.id AND nj.status = 'ready'
                    WHERE newer.document_id = d.id AND newer.version > v.version
                  )
                  AND to_tsvector('simple', c.content) @@ search.q
                ORDER BY ts_rank(to_tsvector('simple', c.content), search.q) DESC, c.id
                LIMIT :limit
            """), {"query": " | ".join(words), "base_id": base_id, "limit": limit * 3})).mappings().all() if words else []
            lexical = [Evidence(**row) for row in rows]
            if vector is None:
                return RetrievalResult(lexical[:limit], "lexical", reason, tokens)
            params = {"base_id": base_id, "model": settings.model, "dimensions": settings.dimensions,
                      "vector": "[" + ",".join(map(str, vector)) + "]", "limit": limit * 3}
            missing = await session.scalar(text("""SELECT EXISTS (
                SELECT 1 FROM knowledge_documents d JOIN knowledge_versions v ON v.document_id=d.id
                JOIN ingestion_jobs i ON i.version_id=v.id AND i.status='ready'
                JOIN knowledge_chunks c ON c.version_id=v.id
                LEFT JOIN knowledge_embeddings e ON e.chunk_id=c.id AND e.model=:model AND e.dimensions=:dimensions
                WHERE d.knowledge_base_id=:base_id AND d.active AND e.chunk_id IS NULL
                  AND NOT EXISTS (SELECT 1 FROM knowledge_versions n JOIN ingestion_jobs ni
                    ON ni.version_id=n.id AND ni.status='ready' WHERE n.document_id=d.id AND n.version>v.version))"""), params)
            if missing:
                return RetrievalResult(lexical[:limit], "lexical", "index_incomplete", tokens)
            rows = (await session.execute(text("""SELECT c.id AS chunk_id, v.id AS version_id, d.id AS document_id,
                d.name AS document_name, v.version, c.content AS excerpt
                FROM knowledge_documents d JOIN knowledge_versions v ON v.document_id=d.id
                JOIN ingestion_jobs i ON i.version_id=v.id AND i.status='ready'
                JOIN knowledge_chunks c ON c.version_id=v.id
                JOIN knowledge_embeddings e ON e.chunk_id=c.id AND e.model=:model AND e.dimensions=:dimensions
                WHERE d.knowledge_base_id=:base_id AND d.active
                  AND NOT EXISTS (SELECT 1 FROM knowledge_versions n JOIN ingestion_jobs ni
                    ON ni.version_id=n.id AND ni.status='ready' WHERE n.document_id=d.id AND n.version>v.version)
                  AND (e.embedding <=> CAST(:vector AS vector)) <= 0.7
                ORDER BY e.embedding <=> CAST(:vector AS vector), c.id LIMIT :limit"""), params)).mappings().all()
            semantic = [Evidence(**row) for row in rows]
            scores = {}
            for branch in (lexical, semantic):
                for rank, item in enumerate(branch, 1):
                    score, _ = scores.get(item.chunk_id, (0, item))
                    scores[item.chunk_id] = (score + 1 / (60 + rank), item)
            combined = sorted(scores.values(), key=lambda pair: (-pair[0], str(pair[1].chunk_id)))
            return RetrievalResult([item for _, item in combined[:limit]], "hybrid", None, tokens)
