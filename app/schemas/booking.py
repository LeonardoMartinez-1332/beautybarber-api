from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class BookingCreate(BaseModel):
    service_id: int = Field(gt=0)
    start_datetime: datetime
    end_datetime: datetime


class BookingOut(BaseModel):
    id: int
    barber_id: int
    service_id: int
    start_datetime: datetime
    end_datetime: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BookingCancelOut(BaseModel):
    id: int
    status: str

    class Config:
        from_attributes = True