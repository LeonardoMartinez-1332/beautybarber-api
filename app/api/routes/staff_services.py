from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.staff import Staff
from app.models.beauty_service import BeautyService
from app.models.staff_service import StaffService
from app.schemas.staff_service import StaffServiceOut
from app.schemas.staff import StaffOut
from app.schemas.beauty_service import BeautyServiceOut

router = APIRouter(tags=["staff_services"])


@router.post(
    "/staff/{staff_id}/services/{service_id}",
    response_model=StaffServiceOut,
    status_code=status.HTTP_201_CREATED,
)
def assign_service_to_staff(
    staff_id: int,
    service_id: int,
    db: Session = Depends(get_db),
):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    service = db.query(BeautyService).filter(BeautyService.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Beauty service not found")

    # opcional pero recomendable: que pertenezcan al mismo business
    if staff.business_id != service.business_id:
        raise HTTPException(
            status_code=400,
            detail="Staff and beauty service must belong to the same business",
        )

    dup = (
        db.query(StaffService)
        .filter(
            StaffService.staff_id == staff_id,
            StaffService.beauty_service_id == service_id,
        )
        .first()
    )
    if dup:
        raise HTTPException(status_code=409, detail="Service already assigned to staff")

    link = StaffService(
        staff_id=staff_id,
        beauty_service_id=service_id,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.delete(
    "/staff/{staff_id}/services/{service_id}",
    response_model=StaffServiceOut,
)
def unassign_service_from_staff(
    staff_id: int,
    service_id: int,
    db: Session = Depends(get_db),
):
    link = (
        db.query(StaffService)
        .filter(
            StaffService.staff_id == staff_id,
            StaffService.beauty_service_id == service_id,
        )
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Staff-service assignment not found")

    db.delete(link)
    db.commit()
    return link


@router.get(
    "/staff/{staff_id}/services",
    response_model=list[BeautyServiceOut],
)
def get_staff_services(
    staff_id: int,
    db: Session = Depends(get_db),
):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    services = (
        db.query(BeautyService)
        .join(StaffService, StaffService.beauty_service_id == BeautyService.id)
        .filter(StaffService.staff_id == staff_id)
        .order_by(BeautyService.id.asc())
        .all()
    )
    return services


@router.get(
    "/beauty-services/{service_id}/staff",
    response_model=list[StaffOut],
)
def get_service_staff(
    service_id: int,
    db: Session = Depends(get_db),
):
    service = db.query(BeautyService).filter(BeautyService.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Beauty service not found")

    staff_list = (
        db.query(Staff)
        .join(StaffService, StaffService.staff_id == Staff.id)
        .filter(StaffService.beauty_service_id == service_id)
        .order_by(Staff.id.asc())
        .all()
    )
    return staff_list