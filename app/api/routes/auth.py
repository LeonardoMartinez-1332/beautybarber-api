from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserLoginOut
from app.services.auth_service import authenticate_user
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(tags=["auth"])

@router.post("/auth/login", response_model=UserLoginOut)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    result = authenticate_user(db, form_data.username, form_data.password)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    user, access_token = result

    return UserLoginOut(
        access_token=access_token,
        user=user,
    )


@router.get("/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "business_id": current_user.business_id,
    }