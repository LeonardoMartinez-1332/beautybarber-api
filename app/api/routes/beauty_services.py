from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import require_roles, get_current_business_id
from app.models.user import User

from app.db.session import get_db
from app.models.business import Business
from app.models.beauty_service import BeautyService
from app.schemas.beauty_service import (
    BeautyServiceCreate,
    BeautyServiceOut,
    BeautyServiceUpdate,
)

router = APIRouter(tags=["beauty_services"])

# CRUD servicios de belleza (multi-tenant)
@router.post("/beauty-services", response_model=BeautyServiceOut, status_code=status.HTTP_201_CREATED)
def create_beauty_service(
    payload: BeautyServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("business_admin", "super_admin")),
    business_id: int = Depends(get_current_business_id),
):
    service = BeautyService(
        business_id=business_id,
        name=payload.name,
        category=payload.category,
        duration_min=payload.duration_min,
        price=payload.price,
        is_active=True,
    )

    db.add(service)
    db.commit()
    db.refresh(service)
    return service

# listar servicios de belleza por negocio (multi-tenant)
@router.get("/beauty-services", response_model=list[BeautyServiceOut])
def list_beauty_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("business_admin", "staff", "super_admin")),
    business_id: int = Depends(get_current_business_id),
):
    return (
        db.query(BeautyService)
        .filter(BeautyService.business_id == business_id)
        .order_by(BeautyService.id.asc())
        .all()
    )

# obtener un servicio de belleza por id (multi-tenant)
@router.get("/beauty-services/{service_id}", response_model=BeautyServiceOut)
def get_beauty_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("business_admin", "staff", "super_admin")),
    business_id: int = Depends(get_current_business_id),
):
    service = (
        db.query(BeautyService)
        .filter(
            BeautyService.id == service_id,
            BeautyService.business_id == business_id
        )
        .first()
    )

    if not service:
        raise HTTPException(status_code=404, detail="Beauty service not found")

    return service

# actualizar un servicio de belleza por id (multi-tenant)
@router.put("/beauty-services/{service_id}", response_model=BeautyServiceOut)
def update_beauty_service(
    service_id: int,
    payload: BeautyServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("business_admin", "super_admin")),
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

    data = payload.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(service, key, value)

    db.commit()
    db.refresh(service)
    return service

# eliminar un servicio de belleza por id (multi-tenant) - soft delete
@router.delete("/beauty-services/{service_id}", response_model=BeautyServiceOut)
def delete_beauty_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("business_admin", "super_admin")),
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

    service.is_active = False
    db.commit()
    db.refresh(service)
    return service