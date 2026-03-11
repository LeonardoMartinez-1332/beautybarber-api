from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import verify_password, create_access_token


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> tuple[User, str] | None:
    user = get_user_by_email(db, email)

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "business_id": user.business_id,
        "staff_id": user.staff_id,
    }

    access_token = create_access_token(token_data)

    return user, access_token