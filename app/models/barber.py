from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.barber_service import barber_services


class Barber(Base):
    __tablename__ = "barbers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # REALCION CON BUSINESS
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), nullable=False, index=True)

    business = relationship("Business", back_populates="barbers")

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    services = relationship(
        "Service",
        secondary=barber_services,
        back_populates="barbers",
        lazy="selectin",
    )
    availability_rules = relationship(
        "BarberAvailabilityRule",
        back_populates="barber",
        cascade="all, delete-orphan",
        lazy="selectin",
    )