"""HTTP endpoints for on-demand generation and audit."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class GenerationRequest(BaseModel):
    knowledge_base_id: UUID | None


def router_for_generations(jobs):
    router = APIRouter(prefix="/api/tickets/{ticket_id}/generations")

    @router.get("")
    async def list_generations(ticket_id: UUID):
        result = await jobs.list_for_ticket(ticket_id)
        if result is None:
            raise HTTPException(404, "Ticket not found.")
        return result

    @router.post("", status_code=202)
    async def request_generation(ticket_id: UUID, data: GenerationRequest):
        status, job_id = await jobs.request(ticket_id, data.knowledge_base_id)
        if status == "missing":
            raise HTTPException(404, "Ticket or knowledge base not found.")
        if status == "full":
            raise HTTPException(429, "Generation queue is full. Try again later.")
        return {"id": job_id, "status": status}

    return router
