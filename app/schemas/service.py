from pydantic import BaseModel, field_serializer, Field, ConfigDict
from typing import Optional
from decimal import Decimal

# esquema para crear un servicio
class ServiceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    duration_min: int = Field(gt=0)
    price: float = Field(gt=0)

# esquema para actualizar un servicio
# con este update se puede mandar un solo campo a actualizar sin necesidad de mandar todos.
class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    duration_min: Optional[int] = Field(default=None, gt=0)
    price: Optional[float] = Field(default=None, gt=0)
    is_active: Optional[bool] = None

# esquema para la respuesta de un servicio
class ServiceOut(BaseModel):
    id: int
    name: str
    duration_min: int
    price: Decimal
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("price")
    def serialize_price(self, v: Decimal):
        return float(v)

# esquema ligero para listar barberos sin detalles de servicios
class BarberLiteOut(BaseModel):
    id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class ServicePage(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[ServiceOut]

    model_config = ConfigDict(from_attributes=True)