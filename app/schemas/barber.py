from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.service import ServiceOut

# Esquema para crear un barbero
class BarberCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: Optional[str] = None
    email: Optional[str] = None

# Esquema para actualizar barbero (todos opcionales)
class BarberUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

# Esquema de salida completo del barbero, incluyendo servicios
class BarberOut(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    is_active: bool
    services: List[ServiceOut] = []

    class Config:
        from_attributes = True

# Esquema ligero para listar barberos sin detalles de servicios
class BarberLiteOut(BaseModel):
    id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

# Esquema aún más simple para ciertos listados
class BarberOutSimple(BaseModel):
    id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True