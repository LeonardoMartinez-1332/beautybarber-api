from __future__ import annotations

from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, func, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BeautyBooking(Base):
    __tablename__ = "beauty_bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    staff_id: Mapped[int] = mapped_column(
        ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    beauty_service_id: Mapped[int] = mapped_column(
        ForeignKey("beauty_services.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    status: Mapped[str] = mapped_column(
        String(20),
        default="confirmed",
        server_default="confirmed",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    staff = relationship("Staff", back_populates="beauty_bookings")
    beauty_service = relationship("BeautyService", back_populates="beauty_bookings")


Index("ix_beauty_bookings_staff_start", BeautyBooking.staff_id, BeautyBooking.start_datetime)
Index("ix_beauty_bookings_staff_end", BeautyBooking.staff_id, BeautyBooking.end_datetime)