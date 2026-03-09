from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.barber import Barber
from app.models.service import Service
from app.schemas.booking import BookingCreate, BookingOut, BookingCancelOut
from app.services.booking_service import create_booking, cancel_booking

router = APIRouter(tags=["bookings"])


@router.post("/barbers/{barber_id}/bookings", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_barber_booking(
    barber_id: int,
    payload: BookingCreate,
    db: Session = Depends(get_db),
):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barber not found")

    service = db.query(Service).filter(Service.id == payload.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if not service.is_active:
        raise HTTPException(status_code=400, detail="Service is inactive")

    try:
        booking = create_booking(
            session=db,
            barber_id=barber_id,
            service_id=payload.service_id,
            start_dt=payload.start_datetime,
            end_dt=payload.end_datetime,
        )
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/barbers/{barber_id}/bookings/{booking_id}/cancel", response_model=BookingCancelOut)
def cancel_barber_booking(
    barber_id: int,
    booking_id: int,
    db: Session = Depends(get_db),
):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barber not found")

    try:
        booking = cancel_booking(db, booking_id)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))