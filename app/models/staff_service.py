from __future__ import annotations

from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StaffService(Base):
    __tablename__ = "staff_services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    staff_id: Mapped[int] = mapped_column(
        ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    beauty_service_id: Mapped[int] = mapped_column(
        ForeignKey("beauty_services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    staff = relationship("Staff", back_populates="staff_services")
    service = relationship("BeautyService", back_populates="staff_services")