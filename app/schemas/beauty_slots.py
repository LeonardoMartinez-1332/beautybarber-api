from __future__ import annotations

from pydantic import BaseModel


class StaffSlotWindowOut(BaseModel):
    staff_id: int
    staff_name: str
    day_of_week: str
    start_time: str
    end_time: str
    service_duration_min: int
    slots: list[str]
    unavailable_slots: list[str] = []


class BeautyAvailableSlotsOut(BaseModel):
    service_id: int
    service_name: str
    date: str
    day_of_week: str
    items: list[StaffSlotWindowOut]