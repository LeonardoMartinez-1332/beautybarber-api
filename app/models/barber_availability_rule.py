from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BarberAvailabilityRule(Base):
    __tablename__ = "barber_availability_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    barber_id: Mapped[int] = mapped_column(
        ForeignKey("barbers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    barber = relationship("Barber", back_populates="availability_rules")

    # 0..6 (Mon..Sun)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    slot_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
