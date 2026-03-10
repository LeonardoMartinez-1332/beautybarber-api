from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class BeautyServiceBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    category: str | None = Field(default=None, max_length=50)
    duration_min: int = Field(gt=0, le=600)
    price: float = Field(ge=0)


class BeautyServiceCreate(BeautyServiceBase):
    business_id: int = Field(gt=0)


class BeautyServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    category: str | None = Field(default=None, max_length=50)
    duration_min: int | None = Field(default=None, gt=0, le=600)
    price: float | None = Field(default=None, ge=0)
    is_active: bool | None = None


class BeautyServiceOut(BeautyServiceBase):
    id: int
    business_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True