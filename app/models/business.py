from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Identidad (nombre del negocio)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    # Para URLs/identificador único del negocio (muy útil en SaaS)
    slug: Mapped[str] = mapped_column(String(160), nullable=False, unique=True, index=True)

    # Contacto / opcional
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Ubicación / operación
    country: Mapped[str] = mapped_column(String(2), nullable=False, default="MX")
    state: Mapped[str | None] = mapped_column(String(80), nullable=True)
    city: Mapped[str | None] = mapped_column(String(80), nullable=True)

    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="America/Monterrey")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="MXN")

    # SaaS meta
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relación: un Business tiene muchos barbers
    barbers = relationship(
        "Barber",
        back_populates="business",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
