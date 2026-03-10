from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Staff(Base):
    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    specialty: Mapped[str | None] = mapped_column(String(80), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    business = relationship("Business", back_populates="staff")

    staff_services = relationship(
    "StaffService",
    back_populates="staff",
    cascade="all, delete-orphan",
    lazy="selectin",
    )

    availability_rules = relationship(
    "StaffAvailabilityRule",
    back_populates="staff",
    cascade="all, delete-orphan",
    )

    beauty_bookings = relationship(
    "BeautyBooking",
    back_populates="staff",
    cascade="all, delete-orphan",
    )