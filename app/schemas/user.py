from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    business_id: int | None = None
    staff_id: int | None = None
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: str = Field(min_length=3, max_length=30)


class UserOut(BaseModel):
    id: int
    business_id: int | None = None
    staff_id: int | None = None
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut