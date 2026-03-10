from sqlalchemy import Column, Integer, Time, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class StaffAvailabilityRule(Base):
    __tablename__ = "staff_availability_rules"

    id = Column(Integer, primary_key=True, index=True)

    staff_id = Column(
        Integer,
        ForeignKey("staff.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    day_of_week = Column(String, nullable=False)

    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    staff = relationship("Staff", back_populates="availability_rules")