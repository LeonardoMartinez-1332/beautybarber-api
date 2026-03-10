from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class StaffServiceOut(BaseModel):
    id: int
    staff_id: int
    beauty_service_id: int
    created_at: datetime

    class Config:
        from_attributes = True