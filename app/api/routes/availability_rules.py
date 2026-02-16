from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from datetime import datetime, timedelta, date as date_type, time as time_type
from typing import List

from app.core.time_utils import overlaps_time_ranges
from app.core.time_utils import merge_availability_windows


from app.db.session import get_db
from app.models.barber import Barber
from app.models.service import Service
from app.models.barber_availability_rule import BarberAvailabilityRule
from app.schemas.barber_availability import (
    AvailabilityRuleCreate,
    AvailabilityRuleOut,
    AvailabilityRuleUpdate,
    AvailabilitySlotsOut,
    SlotWindowOut,
)

router = APIRouter(tags=["availability"])

# Endpoint para crear una nueva regla de disponibilidad para un barbero
@router.post("/barbers/{barber_id}/availability/rules", response_model=AvailabilityRuleOut, status_code=status.HTTP_201_CREATED)
def create_rule(barber_id: int, payload: AvailabilityRuleCreate, db: Session = Depends(get_db)):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barber not found")

    # validaciones base
    if not (0 <= payload.day_of_week <= 6):
        raise HTTPException(status_code=400, detail="day_of_week must be between 0 and 6")

    if payload.start_time >= payload.end_time:
        raise HTTPException(status_code=400, detail="start_time must be less than end_time")

    if payload.slot_minutes <= 0:
        raise HTTPException(status_code=400, detail="slot_minutes must be greater than 0")

    # evitar duplicado exacto (mismo día + mismo rango + mismo slot)
    dup = (
        db.query(BarberAvailabilityRule)
        .filter(
            BarberAvailabilityRule.barber_id == barber_id,
            BarberAvailabilityRule.day_of_week == payload.day_of_week,
            BarberAvailabilityRule.start_time == payload.start_time,
            BarberAvailabilityRule.end_time == payload.end_time,
            BarberAvailabilityRule.slot_minutes == payload.slot_minutes,
        )
        .first()
    )
    if dup:
        if dup.is_active is False:
            dup.is_active = True
            db.commit()
            db.refresh(dup)
            return dup
        raise HTTPException(status_code=409, detail="Availability rule already exists")

    # VALIDAR TRASLAPES (mismo barber + mismo día, solo activas)
    existing_rules = (
        db.query(BarberAvailabilityRule)
        .filter(
            BarberAvailabilityRule.barber_id == barber_id,
            BarberAvailabilityRule.day_of_week == payload.day_of_week,
            BarberAvailabilityRule.is_active.is_(True),
        )
        .all()
    )

    for er in existing_rules:
        if overlaps_time_ranges(payload.start_time, payload.end_time, er.start_time, er.end_time):
            raise HTTPException(
                status_code=409,
                detail=f"Availability rule overlaps with rule_id={er.id} ({er.start_time.strftime('%H:%M')}-{er.end_time.strftime('%H:%M')})"
            )


    rule = BarberAvailabilityRule(barber_id=barber_id, **payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

# Endpoint para listar las reglas de disponibilidad de un barbero
@router.get("/barbers/{barber_id}/availability/rules", response_model=list[AvailabilityRuleOut])
def list_rules(
    barber_id: int,
    db: Session = Depends(get_db),
    active_only: bool = True,
    day_of_week: int | None = Query(default=None, ge=0, le=6),
    order_by: str = Query(default="id"),
    order: str = Query(default="asc"),
):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barber not found")

    q = db.query(BarberAvailabilityRule).filter(BarberAvailabilityRule.barber_id == barber_id)

    if active_only:
        q = q.filter(BarberAvailabilityRule.is_active.is_(True))

    if day_of_week is not None:
        q = q.filter(BarberAvailabilityRule.day_of_week == day_of_week)

    allowed_order_by = {
        "id": BarberAvailabilityRule.id,
        "day_of_week": BarberAvailabilityRule.day_of_week,
        "start_time": BarberAvailabilityRule.start_time,
        "end_time": BarberAvailabilityRule.end_time,
        "created_at": BarberAvailabilityRule.created_at,
    }

    col = allowed_order_by.get(order_by)
    if not col:
        raise HTTPException(status_code=400, detail=f"Invalid order_by. Allowed: {', '.join(allowed_order_by.keys())}")

    order_lower = order.lower()
    if order_lower not in ("asc", "desc"):
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")

    # orden estable (para paginación)
    q = q.order_by((asc(col) if order_lower == "asc" else desc(col)), asc(BarberAvailabilityRule.id))

    return q.all()

# Endpoint para actualizar una regla de disponibilidad existente
@router.put("/availability/rules/{rule_id}", response_model=AvailabilityRuleOut)
def update_rule(rule_id: int, payload: AvailabilityRuleUpdate, db: Session = Depends(get_db)):
    rule = db.query(BarberAvailabilityRule).filter(BarberAvailabilityRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Availability rule not found")

    data = payload.model_dump(exclude_unset=True)

    # Valores finales (si no vienen en payload, se quedan los actuales)
    final_day = data.get("day_of_week", rule.day_of_week)
    final_start = data.get("start_time", rule.start_time)
    final_end = data.get("end_time", rule.end_time)
    final_slot = data.get("slot_minutes", rule.slot_minutes)
    final_is_active = data.get("is_active", rule.is_active)

    # Validaciones básicas
    if final_start >= final_end:
        raise HTTPException(status_code=400, detail="start_time must be less than end_time")

    if not (0 <= final_day <= 6):
        raise HTTPException(status_code=400, detail="day_of_week must be between 0 and 6")

    if final_slot is not None and final_slot <= 0:
        raise HTTPException(status_code=400, detail="slot_minutes must be greater than 0")

    # Si va a quedar activa, validar duplicados/traslapes
    if final_is_active:
        # 1) Duplicado exacto (excluyendo esta rule)
        dup = (
            db.query(BarberAvailabilityRule)
            .filter(
                BarberAvailabilityRule.barber_id == rule.barber_id,
                BarberAvailabilityRule.day_of_week == final_day,
                BarberAvailabilityRule.start_time == final_start,
                BarberAvailabilityRule.end_time == final_end,
                BarberAvailabilityRule.slot_minutes == final_slot,
                BarberAvailabilityRule.id != rule.id,
            )
            .first()
        )
        if dup:
            if dup.is_active is False:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Exact duplicate exists but is inactive (rule_id={dup.id}). "
                        f"Restore it instead of updating into it."
                    )
                )
            raise HTTPException(status_code=409, detail="Availability rule already exists")

        # 2) Traslapes con otras reglas activas del mismo barber y día
        others = (
            db.query(BarberAvailabilityRule)
            .filter(
                BarberAvailabilityRule.barber_id == rule.barber_id,
                BarberAvailabilityRule.day_of_week == final_day,
                BarberAvailabilityRule.is_active.is_(True),
                BarberAvailabilityRule.id != rule.id,
            )
            .all()
        )

        for r in others:
            if overlaps_time_ranges(final_start, final_end, r.start_time, r.end_time):
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Availability rule overlaps with rule_id={r.id} "
                        f"({r.start_time.strftime('%H:%M')}-{r.end_time.strftime('%H:%M')})"
                    )
                )

    # Aplicar cambios
    for k, v in data.items():
        setattr(rule, k, v)

    db.commit()
    db.refresh(rule)
    return rule

# Endpoint para eliminar (desactivar) una regla de disponibilidad
@router.delete("/availability/rules/{rule_id}", response_model=AvailabilityRuleOut)
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(BarberAvailabilityRule).filter(BarberAvailabilityRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Availability rule not found")

    # soft delete
    rule.is_active = False
    db.commit()
    db.refresh(rule)
    return rule

# Endpoint para obtener los slots disponibles de un barbero en una fecha específica, opcionalmente filtrados por servicio
def _generate_time_slots_for_window(
    target_date: date_type,
    start_time: time_type,
    end_time: time_type,
    step_minutes: int,
    service_duration_min: int | None = None,
) -> List[str]:
    """
    Genera slots "HH:MM" para una ventana [start_time, end_time).

    - step_minutes: tamaño del slot (ej. 15, 30)
    - service_duration_min: si se envía, el servicio debe caber completo
        dentro de la ventana para que el slot sea válido.
    """

    # Validaciones defensivas
    if step_minutes <= 0:
        raise ValueError("step_minutes must be > 0")

    if service_duration_min is not None and service_duration_min <= 0:
        raise ValueError("service_duration_min must be > 0")

    start_dt = datetime.combine(target_date, start_time)
    end_dt = datetime.combine(target_date, end_time)

    # si por algún motivo viene invertido (aunque ya lo validas arriba)
    if start_dt >= end_dt:
        return []

    step = timedelta(minutes=step_minutes)
    dur = timedelta(minutes=service_duration_min) if service_duration_min else None

    slots: list[str] = []
    cur = start_dt

    while cur < end_dt:
        if dur:
            if cur + dur <= end_dt:
                slots.append(cur.strftime("%H:%M"))
        else:
            slots.append(cur.strftime("%H:%M"))
        cur += step

    return slots

@router.get("/barbers/{barber_id}/availability/slots", response_model=AvailabilitySlotsOut)
def get_slots(
    barber_id: int,
    date: str = Query(..., description="YYYY-MM-DD"),
    service_id: int | None = Query(default=None),
    merge_windows: bool = Query(default=True, description="Fusiona ventanas pegadas/traslapadas (solo si slot_minutes coincide)"),
    db: Session = Depends(get_db),
):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barber not found")

    # parse fecha
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    day_of_week = target_date.weekday()

    # duración del servicio
    duration_min: int | None = None
    if service_id is not None:
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        if not service.is_active:
            raise HTTPException(status_code=400, detail="Service is inactive")
        if service.duration_min <= 0:
            raise HTTPException(status_code=400, detail="Service duration_min must be > 0")
        duration_min = service.duration_min

    # reglas activas del día
    rules = (
        db.query(BarberAvailabilityRule)
        .filter(
            BarberAvailabilityRule.barber_id == barber_id,
            BarberAvailabilityRule.day_of_week == day_of_week,
            BarberAvailabilityRule.is_active.is_(True),
        )
        .order_by(asc(BarberAvailabilityRule.start_time))
        .all()
    )

    # cerrado si no hay reglas
    if not rules:
        return AvailabilitySlotsOut(
            date=target_date,
            barber_id=barber_id,
            day_of_week=day_of_week,
            is_closed=True,
            service_id=service_id,
            duration_min=duration_min,
            items=[],
            slots=[],
        )

    # windows: o rules tal cual, o mergeadas
    if merge_windows:
        windows = merge_availability_windows(rules)  # dicts {start_time,end_time,slot_minutes}
    else:
        windows = [
            {"start_time": r.start_time, "end_time": r.end_time, "slot_minutes": r.slot_minutes}
            for r in rules
        ]

    items: list[SlotWindowOut] = []
    slots_flat: list[str] = []

    for w in windows:
        window_slots = _generate_time_slots_for_window(
            target_date=target_date,
            start_time=w["start_time"],
            end_time=w["end_time"],
            step_minutes=w["slot_minutes"],
            service_duration_min=duration_min,
        )

        items.append(
            SlotWindowOut(
                start_time=w["start_time"].strftime("%H:%M"),
                end_time=w["end_time"].strftime("%H:%M"),
                slot_minutes=w["slot_minutes"],
                slots=window_slots,
                unavailable_slots=[],  # por ahora vacío, luego aquí bloqueamos por bookings/exceptions
            )
        )

        slots_flat.extend(window_slots)

    slots_unique_sorted = sorted(set(slots_flat))

    return AvailabilitySlotsOut(
        date=target_date,
        barber_id=barber_id,
        day_of_week=day_of_week,
        is_closed=False,
        service_id=service_id,
        duration_min=duration_min,
        items=items,
        slots=slots_unique_sorted,
    )