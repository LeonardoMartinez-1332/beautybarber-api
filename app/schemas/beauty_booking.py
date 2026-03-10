from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class BeautyBookingCreate(BaseModel):
    staff_id: int = Field(gt=0)
    beauty_service_id: int = Field(gt=0)
    start_datetime: datetime
    end_datetime: datetime


class BeautyBookingOut(BaseModel):
    id: int
    staff_id: int
    beauty_service_id: int
    start_datetime: datetime
    end_datetime: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BeautyBookingCancelOut(BaseModel):
    id: int
    status: str

    class Config:
        from_attributes = True