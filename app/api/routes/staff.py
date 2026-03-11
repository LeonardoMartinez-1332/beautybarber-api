from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import require_roles, get_current_business_id
from app.models.user import User

from app.db.session import get_db
from app.models.staff import Staff
from app.models.business import Business
from app.schemas.staff import StaffCreate, StaffOut, StaffUpdate

router = APIRouter(tags=["staff"])

@router.post("/staff", response_model=StaffOut, status_code=status.HTTP_201_CREATED)
def create_staff(
    payload: StaffCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("business_admin", "super_admin")),
    business_id: int = Depends(get_current_business_id),
):
    staff = Staff(
        business_id=business_id,
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        specialty=payload.specialty,
        is_active=True,
    )

    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff

@router.get("/staff", response_model=list[StaffOut])
def list_staff(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("business_admin", "staff", "super_admin")),
    business_id: int = Depends(get_current_business_id),
):
    return (
        db.query(Staff)
        .filter(Staff.business_id == business_id, Staff.is_active == True)
        .order_by(Staff.id.asc())
        .all()
    )

@router.get("/staff/{staff_id}", response_model=StaffOut)
def get_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("business_admin", "staff", "super_admin")),
    business_id: int = Depends(get_current_business_id),
):
    staff = (
        db.query(Staff)
        .filter(
            Staff.id == staff_id,
            Staff.business_id == business_id,
        )
        .first()
    )

    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    return staff

@router.put("/staff/{staff_id}", response_model=StaffOut)
def update_staff(
    staff_id: int,
    payload: StaffUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("business_admin", "super_admin")),
    business_id: int = Depends(get_current_business_id),
):
    staff = (
        db.query(Staff)
        .filter(
            Staff.id == staff_id,
            Staff.business_id == business_id,
        )
        .first()
    )

    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    data = payload.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(staff, key, value)

    db.commit()
    db.refresh(staff)
    return staff

@router.delete("/staff/{staff_id}", response_model=StaffOut)
def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("business_admin", "super_admin")),
    business_id: int = Depends(get_current_business_id),
):
    staff = (
        db.query(Staff)
        .filter(
            Staff.id == staff_id,
            Staff.business_id == business_id,
        )
        .first()
    )

    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    staff.is_active = False
    db.commit()
    db.refresh(staff)
    return staff