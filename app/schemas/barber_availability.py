from datetime import time, datetime, date
from pydantic import BaseModel, Field

# Schemas para las reglas de disponibilidad de barberos
class AvailabilityRuleBase(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    slot_minutes: int = Field(default=30, ge=5, le=240)

# Schema para crear una nueva regla de disponibilidad
class AvailabilityRuleCreate(AvailabilityRuleBase):
    pass

# Schema para actualizar una regla de disponibilidad existente
class AvailabilityRuleUpdate(BaseModel):
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    start_time: time | None = None
    end_time: time | None = None
    slot_minutes: int | None = Field(default=None, ge=5, le=240)
    is_active: bool | None = None

# Schema para leer una regla de disponibilidad
class AvailabilityRuleOut(AvailabilityRuleBase):
    id: int
    barber_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Schemas para las ventanas de disponibilidad y los slots generados
class SlotWindowOut(BaseModel):
    start_time: str   # "10:00"
    end_time: str     # "14:00"
    slot_minutes: int
    slots: list[str]  # ["10:00", "10:30", ...]
    unavailable_slots: list[str] = [] # slots que no están disponibles por reservas u otras reglas

# Schema para la respuesta de disponibilidad de un barbero en un día específico
class AvailabilitySlotsOut(BaseModel):
    date: date
    barber_id: int
    day_of_week: int
    is_closed: bool = False # si no hay reglas activas, se asume que el barbero está cerrado ese día
    service_id: int | None = None
    duration_min: int | None = None
    items: list[SlotWindowOut]
    slots: list[str]  # plano, sin duplicados y ordenado