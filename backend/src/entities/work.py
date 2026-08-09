from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.entities.categories import WorkCategory


class WorkStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class WorkCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=1, max_length=2000)
    category: WorkCategory
    owner_id: UUID
    tags: list[str] = Field(default_factory=list, max_length=12)
    file_url: str = Field(min_length=1, max_length=500)
    thumbnail_url: str | None = Field(default=None, max_length=500)
    downloads_allowed: bool = False


class WorkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    category: WorkCategory
    owner_id: UUID
    tags: list[str]
    file_url: str
    thumbnail_url: str | None
    downloads_allowed: bool
    status: WorkStatus
    created_at: datetime
    updated_at: datetime


class WorkModerationRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)
