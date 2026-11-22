"""HTTP contracts for classification option management."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OptionCreate(BaseModel):
    kind: Literal["category", "priority"]
    name: str
    color: str = Field(default="#64748B", pattern=r"^#[0-9A-Fa-f]{6}$")

    @field_validator("name")
    @classmethod
    def nonblank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name must not be blank")
        return value


class OptionUpdate(BaseModel):
    name: str | None = None
    active: bool | None = None
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")

    @field_validator("name")
    @classmethod
    def nonblank(cls, value: str | None) -> str:
        if value is None or not value.strip():
            raise ValueError("Name must not be blank")
        return value.strip()


class OptionView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kind: Literal["category", "priority"]
    name: str
    active: bool
    color: str
