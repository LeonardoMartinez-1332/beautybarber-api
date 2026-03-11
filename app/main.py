from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.barbers import router as barbers_router
from app.api.routes.services import router as services_router
from app.api.routes.availability_rules import router as availability_rules_router
from app.api.routes.booking import router as booking_router
from app.api.routes.staff import router as staff_router
from app.api.routes.beauty_services import router as beauty_services_router
from app.api.routes.staff_services import router as staff_services_router
from app.api.routes.staff_availability_rules import router as staff_availability_router
from app.api.routes.beauty_slots import router as beauty_slots_router
from app.api.routes.beauty_bookings import router as beauty_bookings_router
from app.api.routes.auth import router as auth_router

app = FastAPI(title="BeautyBarber API")

# Health / utilidades
app.include_router(health_router, prefix="/api", tags=["health"])

# Recursos principales
app.include_router(barbers_router, prefix="/api/barbers", tags=["barbers"])
app.include_router(services_router, prefix="/api/services", tags=["services"])
app.include_router(availability_rules_router, prefix="/api", tags=["availability"])
app.include_router(booking_router, prefix="/api", tags=["bookings"])
app.include_router(staff_router, prefix="/api", tags=["staff"])
app.include_router(beauty_services_router, prefix="/api", tags=["beauty_services"])
app.include_router(staff_services_router, prefix="/api", tags=["staff_services"])
app.include_router(staff_availability_router, prefix="/api", tags=["staff availability"])
app.include_router(beauty_slots_router, prefix="/api", tags=["beauty_slots"])
app.include_router(beauty_bookings_router, prefix="/api", tags=["beauty_bookings"])
app.include_router(auth_router, prefix="/api", tags=["auth"])