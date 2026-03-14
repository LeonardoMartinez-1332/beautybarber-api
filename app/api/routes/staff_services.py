from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import require_roles, get_current_business_id
from app.models.user import User
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.staff import Staff
from app.models.beauty_service import BeautyService
from app.models.staff_service import StaffService
from app.schemas.staff_service import StaffServiceOut
from app.schemas.staff import StaffOut
from app.schemas.beauty_service import BeautyServiceOut

router = APIRouter(tags=["staff_services"])

# endponits para asignar y desasignar servicios a staff, y para listar los servicios de un staff y el staff de un servicio
@router.post(
    "/staff/{staff_id}/services/{service_id}",
    response_model=StaffServiceOut,
    status_code=status.HTTP_201_CREATED,
)
def assign_service_to_staff(
    staff_id: int,
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("business_admin", "super_admin")),
    business_id: int = Depends(get_current_business_id),
):
    staff = (
        db.query(Staff)
        .filter(
            Staff.id == staff_id,
            Staff.business_id == business_id,
        )
        .first()
    )
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    service = (
        db.query(BeautyService)
        .filter(
            BeautyService.id == service_id,
            BeautyService.business_id == business_id,
        )
        .first()
    )
    if not service:
        raise HTTPException(status_code=404, detail="Beauty service not found")

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

# endpoint para desasignar un servicio de un staff, se borra el registro de la tabla intermedia StaffService
@router.delete(
    "/staff/{staff_id}/services/{service_id}",
    response_model=StaffServiceOut,
)
def unassign_service_from_staff(
    staff_id: int,
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("business_admin", "super_admin")),
    business_id: int = Depends(get_current_business_id),
):
    staff = (
        db.query(Staff)
        .filter(
            Staff.id == staff_id,
            Staff.business_id == business_id,
        )
        .first()
    )
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    service = (
        db.query(BeautyService)
        .filter(
            BeautyService.id == service_id,
            BeautyService.business_id == business_id,
        )
        .first()
    )
    if not service:
        raise HTTPException(status_code=404, detail="Beauty service not found")

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

# endpoint para listar los servicios asignados a un staff, se hace un join entre StaffService y BeautyService 
# para obtener los detalles de los servicios
@router.get(
    "/staff/{staff_id}/services",
    response_model=list[BeautyServiceOut],
)
def get_staff_services(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("business_admin", "staff", "super_admin")),
    business_id: int = Depends(get_current_business_id),
):
    staff = (
        db.query(Staff)
        .filter(
            Staff.id == staff_id,
            Staff.business_id == business_id,
        )
        .first()
    )
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    services = (
        db.query(BeautyService)
        .join(StaffService, StaffService.beauty_service_id == BeautyService.id)
        .filter(
            StaffService.staff_id == staff_id,
            BeautyService.business_id == business_id,
        )
        .order_by(BeautyService.id.asc())
        .all()
    )
    return services

# endpoint para listar el staff asignado a un servicio, se hace un join entre StaffService y Staff para obtener los detalles del staff, 
# se ordena por id ascendente para mantener un orden consistente en la respuesta
@router.get(
    "/beauty-services/{service_id}/staff",
    response_model=list[StaffOut],
)
def get_service_staff(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("business_admin", "staff", "super_admin")),
    business_id: int = Depends(get_current_business_id),
):
    service = (
        db.query(BeautyService)
        .filter(
            BeautyService.id == service_id,
            BeautyService.business_id == business_id,
        )
        .first()
    )
    if not service:
        raise HTTPException(status_code=404, detail="Beauty service not found")

    staff_list = (
        db.query(Staff)
        .join(StaffService, StaffService.staff_id == Staff.id)
        .filter(
            StaffService.beauty_service_id == service_id,
            Staff.business_id == business_id,
        )
        .order_by(Staff.id.asc())
        .all()
    )
    return staff_list