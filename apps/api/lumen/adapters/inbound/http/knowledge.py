"""HTTP API for versioned knowledge content."""

from pathlib import PurePath
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field, field_validator

from lumen.application.knowledge import Knowledge


class BaseCreate(BaseModel):
    name: str = Field(max_length=200)

    @field_validator("name")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip() or "\x00" in value:
            raise ValueError("Name must not be blank.")
        return value.strip()


class ActiveWrite(BaseModel):
    active: bool


def router_for_knowledge(knowledge: Knowledge) -> APIRouter:
    router = APIRouter(prefix="/api/knowledge")

    async def content_from(request: Request, filename: str | None) -> str:
        if filename is not None and PurePath(filename).suffix.lower() not in (".txt", ".md"):
            raise HTTPException(422, "Only .txt and .md files are supported.")
        raw = bytearray()
        async for part in request.stream():
            raw.extend(part)
            if len(raw) > knowledge.max_bytes:
                raise HTTPException(413, "Content exceeds the configured size limit.")
        try:
            return knowledge.validate_content(raw.decode("utf-8-sig"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise HTTPException(422, "Content must be nonblank UTF-8 text without NUL characters.") from exc

    @router.get("/bases")
    async def list_bases():
        return await knowledge.store.list_bases()

    @router.post("/bases", status_code=201)
    async def create_base(data: BaseCreate):
        return await knowledge.store.create_base(data.name)

    @router.get("/bases/{base_id}/documents")
    async def list_documents(base_id: UUID):
        result = await knowledge.store.list_documents(base_id)
        if result is None:
            raise HTTPException(404, "Knowledge base not found.")
        return result

    @router.post("/bases/{base_id}/documents", status_code=201)
    async def create_document(base_id: UUID, request: Request, name: str = Query(min_length=1, max_length=200), filename: str | None = Query(default=None, max_length=255)):
        clean_name = name.strip()
        if not clean_name or "\x00" in clean_name:
            raise HTTPException(422, "Name must not be blank.")
        result = await knowledge.store.create_document(base_id, clean_name, await content_from(request, filename))
        if result is None:
            raise HTTPException(404, "Knowledge base not found.")
        return result

    @router.post("/documents/{document_id}/versions", status_code=201)
    async def add_version(document_id: UUID, request: Request, filename: str | None = Query(default=None, max_length=255)):
        result = await knowledge.store.add_version(document_id, await content_from(request, filename))
        if result is None:
            raise HTTPException(404, "Document not found.")
        return result

    @router.patch("/documents/{document_id}")
    async def set_active(document_id: UUID, data: ActiveWrite):
        result = await knowledge.store.set_active(document_id, data.active)
        if result is None:
            raise HTTPException(404, "Document not found.")
        return result

    @router.get("/versions/{version_id}")
    async def get_version(version_id: UUID):
        result = await knowledge.store.get_version(version_id)
        if result is None:
            raise HTTPException(404, "Version not found.")
        return result

    @router.post("/versions/{version_id}/retry", status_code=202)
    async def retry(version_id: UUID):
        result = await knowledge.store.retry(version_id)
        if result == "missing":
            raise HTTPException(404, "Version not found.")
        if result == "conflict":
            raise HTTPException(409, "Ingestion is not in a failed state.")
        return {"status": result}

    @router.post("/versions/{version_id}/semantic-retry", status_code=202)
    async def retry_semantic(version_id: UUID):
        result = await knowledge.store.retry_semantic(version_id)
        if result == "conflict":
            raise HTTPException(409, "Semantic indexing is not in a failed state.")
        return {"status": result}

    return router
