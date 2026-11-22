"""HTTP request and response contracts for tickets."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from lumen.adapters.inbound.http.options import OptionView


class TicketCreate(BaseModel):
    subject: str
    description: str

    @field_validator("subject", "description")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Must not be empty or whitespace only")
        return value


class ClassificationWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=0)
    category_ids: list[UUID] | None = None
    priority_id: UUID | None = None


class ResponseWrite(BaseModel):
    text: str
    expected_revision: int | None = Field(ge=1)
    adopted_generation_id: UUID | None = None

    @field_validator("text")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Must not be empty or whitespace only")
        return value


class ResponseView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: UUID
    text: str
    status: str
    edited_at: datetime
    revision: int
    adopted_generation_id: UUID | None
    provenance: str


class TicketDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subject: str
    description: str
    received_at: datetime
    classification_status: str
    classification_result: str | None
    classification_source: str | None
    classification_categories: list[OptionView]
    classification_priority: OptionView | None
    classification_failure_reason: str | None
    effective_categories: list[OptionView]
    effective_priority: OptionView | None
    category_origin: str | None
    priority_origin: str | None
    classification_revision: int


class TicketSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subject: str
    received_at: datetime
    classification_status: str
    classification_source: str | None
    classification_result: str | None
    classification_categories: list[OptionView]
    classification_priority: OptionView | None
    effective_categories: list[OptionView]
    effective_priority: OptionView | None
    category_origin: str | None
    priority_origin: str | None
    classification_revision: int


class TicketPage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[TicketSummary]
    page: int
    page_size: int
    total: int
