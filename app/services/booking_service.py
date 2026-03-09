from __future__ import annotations
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.models.booking import Booking


def has_overlap(session: Session, barber_id: int, start_dt: datetime, end_dt: datetime) -> bool:
    # overlap: existing.start < new_end AND existing.end > new_start
    stmt = (
        select(Booking.id)
        .where(
            Booking.barber_id == barber_id,
            Booking.status == "confirmed",
            Booking.start_datetime < end_dt,
            Booking.end_datetime > start_dt,
        )
        .limit(1)
    )
    return session.execute(stmt).first() is not None


def create_booking(session: Session, barber_id: int, service_id: int, start_dt: datetime, end_dt: datetime) -> Booking:
    if end_dt <= start_dt:
        raise ValueError("end_datetime must be greater than start_datetime")

    if has_overlap(session, barber_id, start_dt, end_dt):
        raise ValueError("Slot is already booked")

    booking = Booking(
        barber_id=barber_id,
        service_id=service_id,
        start_datetime=start_dt,
        end_datetime=end_dt,
        status="confirmed",
    )
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking


def list_bookings_in_range(session: Session, barber_id: int, start_dt: datetime, end_dt: datetime) -> list[Booking]:
    stmt = (
        select(Booking)
        .where(
            Booking.barber_id == barber_id,
            Booking.status == "confirmed",
            Booking.start_datetime < end_dt,
            Booking.end_datetime > start_dt,
        )
        .order_by(Booking.start_datetime.asc())
    )
    return list(session.execute(stmt).scalars().all())


def cancel_booking(session: Session, booking_id: int) -> Booking:
    booking = session.get(Booking, booking_id)
    if not booking:
        raise ValueError("Booking not found")

    booking.status = "cancelled"
    session.commit()
    session.refresh(booking)
    return booking