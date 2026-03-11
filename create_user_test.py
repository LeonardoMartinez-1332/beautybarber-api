from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password

db = SessionLocal()

user = User(
    business_id=1,
    staff_id=None,
    name="Admin Salon",
    email="admin@salon.com",
    password_hash=hash_password("123456"),
    role="business_admin",
    is_active=True,
)

db.add(user)
db.commit()
db.refresh(user)

print("Usuario creado:", user.id, user.email)

db.close()