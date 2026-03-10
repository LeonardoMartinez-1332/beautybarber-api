from __future__ import annotations

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.beauty_booking import BeautyBooking


def has_overlap(session: Session, staff_id: int, start_dt: datetime, end_dt: datetime) -> bool:
    stmt = (
        select(BeautyBooking.id)
        .where(
            BeautyBooking.staff_id == staff_id,
            BeautyBooking.status == "confirmed",
            BeautyBooking.start_datetime < end_dt,
            BeautyBooking.end_datetime > start_dt,
        )
        .limit(1)
    )
    return session.execute(stmt).first() is not None


def create_beauty_booking(
    session: Session,
    staff_id: int,
    beauty_service_id: int,
    start_dt: datetime,
    end_dt: datetime,
) -> BeautyBooking:
    if end_dt <= start_dt:
        raise ValueError("end_datetime must be greater than start_datetime")

    if has_overlap(session, staff_id, start_dt, end_dt):
        raise ValueError("Slot is already booked")

    booking = BeautyBooking(
        staff_id=staff_id,
        beauty_service_id=beauty_service_id,
        start_datetime=start_dt,
        end_datetime=end_dt,
        status="confirmed",
    )

    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking


def cancel_beauty_booking(session: Session, booking_id: int) -> BeautyBooking:
    booking = session.get(BeautyBooking, booking_id)
    if not booking:
        raise ValueError("Beauty booking not found")

    booking.status = "cancelled"
    session.commit()
    session.refresh(booking)
    return booking