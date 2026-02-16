from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc, desc, func, distinct
from typing import Optional

from app.db.session import get_db
from app.models.barber import Barber
from app.models.service import Service
from app.schemas.barber import BarberCreate, BarberOut, BarberUpdate, BarberOutSimple

from app.schemas.service import ServiceOut
from app.schemas.service import ServicePage

router = APIRouter(tags=["barbers"])

# endpoint para crear un barbero
@router.post("", response_model=BarberOut, status_code=status.HTTP_201_CREATED)
def create_barber(payload: BarberCreate, db: Session = Depends(get_db)):
    barber = Barber(**payload.model_dump())
    db.add(barber)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    db.refresh(barber)
    return barber

# endpoint para listar barberos (por default: activos)
@router.get("", response_model=list[BarberOut])
def list_barbers(db: Session = Depends(get_db), active_only: bool = True):
    q = db.query(Barber)
    if active_only:
        q = q.filter(Barber.is_active == True)
    return q.all()

# endpoint para traer un barbero por id
@router.get("/{barber_id}", response_model=BarberOut)
def get_barber(barber_id: int, db: Session = Depends(get_db)):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barber not found")
    return barber

# endpoint para actualizar barbero
@router.put("/{barber_id}", response_model=BarberOut)
def update_barber(barber_id: int, payload: BarberUpdate, db: Session = Depends(get_db)):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barber not found")

    data = payload.model_dump(exclude_unset=True)

    # si cambia email, puede pegarle al UNIQUE -> capturamos con IntegrityError
    for k, v in data.items():
        setattr(barber, k, v)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    db.refresh(barber)
    return barber

# endpoint para "eliminar" (soft delete)
@router.delete("/{barber_id}", response_model=BarberOut)
def delete_barber(barber_id: int, db: Session = Depends(get_db)):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barber not found")

    barber.is_active = False

    db.commit()
    db.refresh(barber)
    return barber

# endpoint para asignar un servicio a un barbero
@router.post("/{barber_id}/services/{service_id}", response_model=BarberOut)
def assign_service(barber_id: int, service_id: int, db: Session = Depends(get_db)):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barber not found")

    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if service in barber.services:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service already assigned to this barber"
        )

    barber.services.append(service)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service already assigned to this barber"
        )

    db.refresh(barber)
    return barber

# endpoint para desasignar un servicio de un barbero
@router.delete("/{barber_id}/services/{service_id}", response_model=BarberOut, status_code=status.HTTP_200_OK)
def unassign_service(barber_id: int, service_id: int, db: Session = Depends(get_db)):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barber not found")

    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Si no está asignado, 409 (conflicto de estado)
    if service not in barber.services:
        raise HTTPException(status_code=409, detail="Service is not assigned to this barber")

    barber.services.remove(service)
    db.commit()
    db.refresh(barber)
    return barber

# endpoint para listar servicios asignados a un barbero con filtros y ordenamiento
@router.get("/{barber_id}/services", response_model=ServicePage)
def get_barber_services(
    barber_id: int,
    db: Session = Depends(get_db),
    active_only: bool = True,
    price_min: float | None = Query(None, ge=0),
    price_max: float | None = Query(None, ge=0),
    duration_min: int | None = Query(None, ge=0),
    duration_max: int | None = Query(None, ge=0),
    order_by: str = Query("id", pattern="^(id|name|price|duration_min)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    exists = db.query(Barber.id).filter(Barber.id == barber_id).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Barber not found")

    if price_min is not None and price_max is not None and price_min > price_max:
        raise HTTPException(status_code=422, detail="price_min cannot be greater than price_max")

    # Base query (sin orden todavía)
    q = (
        db.query(Service)
        .join(Service.barbers)
        .filter(Barber.id == barber_id)
    )

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

    total = (
        q.order_by(None)
            .with_entities(func.count(distinct(Service.id)))
            .scalar()
    )

    # Orden principal (whitelist)
    cols = {
        "id": Service.id,
        "name": Service.name,
        "price": Service.price,
        "duration_min": Service.duration_min,
    }
    primary_col = cols[order_by]
    primary_order = asc(primary_col) if order == "asc" else desc(primary_col)

    # items con orden estable:
    # 1) orden principal por campo elegido
    # 2) orden secundario por id (si hay empates no “brinca” la paginación)
    q_items = q.order_by(primary_order, Service.id.asc())

    items = (
        q_items.distinct()
            .offset(offset)
            .limit(limit)
            .all()
    )

    return {"total": total, "limit": limit, "offset": offset, "items": items}

# endpoint para listar barberos asignados a un servicio
@router.get("/{service_id}/barbers", response_model=list[BarberOutSimple])
def get_service_barbers(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    #si el servico está inactivo, se decide si se esconde
    if not service.is_active:
        raise HTTPException(status_code=404, detail="Service not found")

    return service.barbers