from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc, desc

from app.db.session import get_db
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceOut, ServiceUpdate, BarberLiteOut

router = APIRouter(tags=["services"])

# Crear un servicio
@router.post("", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db)):
    # opcional: si ya existe inactivo -> reactivar en vez de 409
    existing = db.query(Service).filter(Service.name == payload.name).first()
    if existing:
        if existing.is_active is False:
            existing.is_active = True
            existing.duration_min = payload.duration_min
            existing.price = payload.price
            db.commit()
            db.refresh(existing)
            return existing
        raise HTTPException(status_code=409, detail="Service name already exists")

    service = Service(**payload.model_dump())
    db.add(service)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Service name already exists")

    db.refresh(service)
    return service

# Listar servicios con filtros y ordenamiento
@router.get("", response_model=list[ServiceOut])
def list_services(
    db: Session = Depends(get_db),
    active_only: bool = True,

    # filtros
    price_min: float | None = Query(default=None, ge=0),
    price_max: float | None = Query(default=None, ge=0),
    duration_min: int | None = Query(default=None, ge=0),
    duration_max: int | None = Query(default=None, ge=0),

    # ordenamiento
    order_by: str = Query(default="id"),
    order: str = Query(default="asc"),
):
    q = db.query(Service)

    # filtros
    if active_only:
        q = q.filter(Service.is_active.is_(True))

    if price_min is not None:
        q = q.filter(Service.price >= price_min)

    if price_max is not None:
        q = q.filter(Service.price <= price_max)

    if duration_min is not None:
        q = q.filter(Service.duration_min >= duration_min)

    if duration_max is not None:
        q = q.filter(Service.duration_min <= duration_max)

    # validaciones cruzadas
    if price_min is not None and price_max is not None and price_min > price_max:
        raise HTTPException(status_code=400, detail="price_min cannot be greater than price_max")

    if duration_min is not None and duration_max is not None and duration_min > duration_max:
        raise HTTPException(status_code=400, detail="duration_min cannot be greater than duration_max")

    # ordenamiento
    allowed_order_by = {
        "id": Service.id,
        "name": Service.name,
        "price": Service.price,
        "duration_min": Service.duration_min,
        "created_at": Service.created_at,
    }

    col = allowed_order_by.get(order_by)
    if not col:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid order_by. Allowed: {', '.join(allowed_order_by.keys())}"
        )

    order_lower = order.lower()
    if order_lower not in ("asc", "desc"):
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")

    q = q.order_by(asc(col) if order_lower == "asc" else desc(col))

    return q.all()

# Obtener un servicio por ID
@router.get("/{service_id}", response_model=ServiceOut)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

# Actualizar un servicio
@router.put("/{service_id}", response_model=ServiceOut)
def update_service(service_id: int, payload: ServiceUpdate, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    data = payload.model_dump(exclude_unset=True)

    if "name" in data:
        dup = db.query(Service).filter(Service.name == data["name"], Service.id != service_id).first()
        if dup:
            raise HTTPException(status_code=409, detail="Service name already exists")

    for k, v in data.items():
        setattr(service, k, v)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Service name already exists")

    db.refresh(service)
    return service

# Restaurar un servicio
@router.patch("/{service_id}/restore", response_model=ServiceOut)
def restore_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service.is_active = True
    db.commit()
    db.refresh(service)
    return service

# Eliminar (desactivar) un servicio
@router.delete("/{service_id}", response_model=ServiceOut)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if not service.is_active:
        return service

    # Soft delete
    service.is_active = False
    db.commit()
    db.refresh(service)
    return service

# Listar servicios asignados a un barbero
@router.get("/{service_id}/barbers", response_model=list[BarberLiteOut])
def get_service_barbers(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return service.barbers

