from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.staff import Staff
from app.models.beauty_service import BeautyService
from app.models.staff_service import StaffService
from app.schemas.beauty_booking import (
    BeautyBookingCreate,
    BeautyBookingOut,
    BeautyBookingCancelOut,
)
from app.services.beauty_booking_service import (
    create_beauty_booking,
    cancel_beauty_booking,
)

router = APIRouter(tags=["beauty_bookings"])


@router.post(
    "/beauty-bookings",
    response_model=BeautyBookingOut,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    payload: BeautyBookingCreate,
    db: Session = Depends(get_db),
):
    staff = db.query(Staff).filter(Staff.id == payload.staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    service = db.query(BeautyService).filter(BeautyService.id == payload.beauty_service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Beauty service not found")

    if not service.is_active:
        raise HTTPException(status_code=400, detail="Beauty service is inactive")

    # validar que ese staff sí pueda hacer ese servicio
    assignment = (
        db.query(StaffService)
        .filter(
            StaffService.staff_id == payload.staff_id,
            StaffService.beauty_service_id == payload.beauty_service_id,
        )
        .first()
    )
    if not assignment:
        raise HTTPException(
            status_code=400,
            detail="This staff member is not assigned to the selected beauty service",
        )

    if staff.business_id != service.business_id:
        raise HTTPException(
            status_code=400,
            detail="Staff and beauty service must belong to the same business",
        )

    try:
        booking = create_beauty_booking(
            session=db,
            staff_id=payload.staff_id,
            beauty_service_id=payload.beauty_service_id,
            start_dt=payload.start_datetime,
            end_dt=payload.end_datetime,
        )
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/beauty-bookings/{booking_id}/cancel",
    response_model=BeautyBookingCancelOut,
)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
):
    try:
        booking = cancel_beauty_booking(db, booking_id)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))