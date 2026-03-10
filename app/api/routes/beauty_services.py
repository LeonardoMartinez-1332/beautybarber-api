from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.business import Business
from app.models.beauty_service import BeautyService
from app.schemas.beauty_service import (
    BeautyServiceCreate,
    BeautyServiceOut,
    BeautyServiceUpdate,
)

router = APIRouter(tags=["beauty_services"])


@router.post("/beauty-services", response_model=BeautyServiceOut, status_code=status.HTTP_201_CREATED)
def create_beauty_service(payload: BeautyServiceCreate, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == payload.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    service = BeautyService(**payload.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get("/beauty-services", response_model=list[BeautyServiceOut])
def list_beauty_services(db: Session = Depends(get_db)):
    return db.query(BeautyService).order_by(BeautyService.id.asc()).all()


@router.get("/beauty-services/{service_id}", response_model=BeautyServiceOut)
def get_beauty_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(BeautyService).filter(BeautyService.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Beauty service not found")
    return service


@router.put("/beauty-services/{service_id}", response_model=BeautyServiceOut)
def update_beauty_service(service_id: int, payload: BeautyServiceUpdate, db: Session = Depends(get_db)):
    service = db.query(BeautyService).filter(BeautyService.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Beauty service not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(service, key, value)

    db.commit()
    db.refresh(service)
    return service


@router.delete("/beauty-services/{service_id}", response_model=BeautyServiceOut)
def delete_beauty_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(BeautyService).filter(BeautyService.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Beauty service not found")

    service.is_active = False
    db.commit()
    db.refresh(service)
    return service