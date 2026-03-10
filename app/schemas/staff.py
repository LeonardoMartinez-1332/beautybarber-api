from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class StaffBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    specialty: str | None = Field(default=None, max_length=80)


class StaffCreate(StaffBase):
    business_id: int = Field(gt=0)


class StaffUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    specialty: str | None = Field(default=None, max_length=80)
    is_active: bool | None = None


class StaffOut(StaffBase):
    id: int
    business_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True