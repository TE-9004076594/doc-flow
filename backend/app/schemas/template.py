"""Template and template version schemas."""

from datetime import datetime
from pydantic import BaseModel
from typing import Any


class TemplateCreate(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    tags: list[str] = []


class TemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    status: str | None = None


class TemplateResponse(BaseModel):
    id: str
    name: str
    description: str | None
    category: str | None
    tags: list[Any]
    status: str
    current_version: int
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateVersionResponse(BaseModel):
    id: str
    template_id: str
    version_number: int
    change_description: str | None
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True
