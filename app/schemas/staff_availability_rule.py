from datetime import time
from pydantic import BaseModel


class StaffAvailabilityRuleCreate(BaseModel):
    staff_id: int
    day_of_week: str
    start_time: time
    end_time: time


class StaffAvailabilityRuleOut(StaffAvailabilityRuleCreate):
    id: int

    class Config:
        from_attributes = True