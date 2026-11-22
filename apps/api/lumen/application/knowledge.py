"""Knowledge operations independent of HTTP and persistence."""

from typing import Protocol
from uuid import UUID


class KnowledgeStore(Protocol):
    async def list_bases(self): ...
    async def create_base(self, name: str): ...
    async def list_documents(self, base_id: UUID): ...
    async def create_document(self, base_id: UUID, name: str, content: str): ...
    async def add_version(self, document_id: UUID, content: str): ...
    async def set_active(self, document_id: UUID, active: bool): ...
    async def get_version(self, version_id: UUID): ...
    async def retry(self, version_id: UUID): ...


class Knowledge:
    def __init__(self, store: KnowledgeStore, max_bytes: int):
        self.store = store
        self.max_bytes = max_bytes

    def validate_content(self, content: str) -> str:
        if not content.strip() or "\x00" in content:
            raise ValueError("Content must contain nonblank text and no NUL characters.")
        if len(content.encode("utf-8")) > self.max_bytes:
            raise ValueError("Content exceeds the configured size limit.")
        return content
