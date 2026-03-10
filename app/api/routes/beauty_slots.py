from __future__ import annotations

from datetime import datetime, timedelta, time as time_type
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.beauty_service import BeautyService
from app.models.staff import Staff
from app.models.staff_service import StaffService
from app.models.staff_availability_rule import StaffAvailabilityRule
from app.models.beauty_booking import BeautyBooking
from app.schemas.beauty_slots import BeautyAvailableSlotsOut, StaffSlotWindowOut

router = APIRouter(tags=["beauty_slots"])


DAY_NAME_MAP = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}


def _generate_slots_for_staff_window(
    target_date,
    start_time,
    end_time,
    service_duration_min: int,
) -> list[str]:
    start_dt = datetime.combine(target_date, start_time)
    end_dt = datetime.combine(target_date, end_time)

    if start_dt >= end_dt:
        return []

    duration = timedelta(minutes=service_duration_min)
    cur = start_dt
    slots: list[str] = []

    while cur + duration <= end_dt:
        slots.append(cur.strftime("%H:%M"))
        cur += duration

    return slots


def _slot_overlaps_booking(
    slot_start: datetime,
    slot_end: datetime,
    booking_start: datetime,
    booking_end: datetime,
) -> bool:
    return slot_start < booking_end and booking_start < slot_end


@router.get(
    "/beauty-services/{service_id}/available-slots",
    response_model=BeautyAvailableSlotsOut,
)
def get_beauty_service_available_slots(
    service_id: int,
    date: str = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    service = db.query(BeautyService).filter(BeautyService.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Beauty service not found")

    if not service.is_active:
        raise HTTPException(status_code=400, detail="Beauty service is inactive")

    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    day_of_week = DAY_NAME_MAP[target_date.weekday()]

    # staff que puede hacer este servicio
    staff_list = (
        db.query(Staff)
        .join(StaffService, StaffService.staff_id == Staff.id)
        .filter(
            StaffService.beauty_service_id == service_id,
            Staff.is_active.is_(True),
        )
        .order_by(Staff.id.asc())
        .all()
    )

    if not staff_list:
        return BeautyAvailableSlotsOut(
            service_id=service.id,
            service_name=service.name,
            date=str(target_date),
            day_of_week=day_of_week,
            items=[],
        )

    items: list[StaffSlotWindowOut] = []

    for staff in staff_list:
        rules = (
            db.query(StaffAvailabilityRule)
            .filter(
                StaffAvailabilityRule.staff_id == staff.id,
                StaffAvailabilityRule.day_of_week == day_of_week,
            )
            .order_by(StaffAvailabilityRule.start_time.asc())
            .all()
        )

        if not rules:
            continue

        # timezone del negocio
        local_tz = ZoneInfo(staff.business.timezone or "America/Monterrey")

        # traer bookings confirmados del día para este staff
        day_start = datetime.combine(target_date, time_type.min)
        day_end = datetime.combine(target_date, time_type.max)

        bookings = (
            db.query(BeautyBooking)
            .filter(
                BeautyBooking.staff_id == staff.id,
                BeautyBooking.status == "confirmed",
                BeautyBooking.start_datetime < day_end,
                BeautyBooking.end_datetime > day_start,
            )
            .order_by(BeautyBooking.start_datetime.asc())
            .all()
        )

        for rule in rules:
            all_slots = _generate_slots_for_staff_window(
                target_date=target_date,
                start_time=rule.start_time,
                end_time=rule.end_time,
                service_duration_min=service.duration_min,
            )

            available_slots: list[str] = []
            unavailable_slots: list[str] = []

            for slot_str in all_slots:
                slot_start = datetime.combine(
                    target_date,
                    datetime.strptime(slot_str, "%H:%M").time(),
                )
                slot_end = slot_start + timedelta(minutes=service.duration_min)

                is_occupied = any(
                    _slot_overlaps_booking(
                        slot_start,
                        slot_end,
                        booking.start_datetime.astimezone(local_tz).replace(tzinfo=None),
                        booking.end_datetime.astimezone(local_tz).replace(tzinfo=None),
                    )
                    for booking in bookings
                )

                if is_occupied:
                    unavailable_slots.append(slot_str)
                else:
                    available_slots.append(slot_str)

            items.append(
                StaffSlotWindowOut(
                    staff_id=staff.id,
                    staff_name=staff.name,
                    day_of_week=rule.day_of_week,
                    start_time=rule.start_time.strftime("%H:%M"),
                    end_time=rule.end_time.strftime("%H:%M"),
                    service_duration_min=service.duration_min,
                    slots=available_slots,
                    unavailable_slots=unavailable_slots,
                )
            )

    return BeautyAvailableSlotsOut(
        service_id=service.id,
        service_name=service.name,
        date=str(target_date),
        day_of_week=day_of_week,
        items=items,
    )