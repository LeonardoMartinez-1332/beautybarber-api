from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.staff_availability_rule import StaffAvailabilityRule
from app.schemas.staff_availability_rule import (
    StaffAvailabilityRuleCreate,
    StaffAvailabilityRuleOut
)

router = APIRouter(tags=["staff availability"])


@router.post("/staff/availability", response_model=StaffAvailabilityRuleOut)
def create_rule(data: StaffAvailabilityRuleCreate, db: Session = Depends(get_db)):

    rule = StaffAvailabilityRule(**data.model_dump())

    db.add(rule)
    db.commit()
    db.refresh(rule)

    return rule


@router.get("/staff/{staff_id}/availability", response_model=list[StaffAvailabilityRuleOut])
def get_staff_rules(staff_id: int, db: Session = Depends(get_db)):

    return db.query(StaffAvailabilityRule).filter(
        StaffAvailabilityRule.staff_id == staff_id
    ).all()