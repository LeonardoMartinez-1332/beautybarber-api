# app/models/booking.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base 


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    barber_id: Mapped[int] = mapped_column(ForeignKey("barbers.id", ondelete="CASCADE"), index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="RESTRICT"), index=True)

    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    # confirmar | cancelar
    status: Mapped[str] = mapped_column(String(20), default="confirmed", server_default="confirmed", index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    barber = relationship("Barber", back_populates="bookings")
    service = relationship("Service")

# Índices útiles (performance)
Index("ix_bookings_barber_start", Booking.barber_id, Booking.start_datetime)
Index("ix_bookings_barber_end", Booking.barber_id, Booking.end_datetime)