from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.barbers import router as barbers_router
from app.api.routes.services import router as services_router
from app.api.routes.availability_rules import router as availability_rules_router

app = FastAPI(title="BeautyBarber API")

# Health / utilidades
app.include_router(health_router, prefix="/api", tags=["health"])

# Recursos principales
app.include_router(barbers_router, prefix="/api/barbers", tags=["barbers"])
app.include_router(services_router, prefix="/api/services", tags=["services"])
app.include_router(availability_rules_router, prefix="/api", tags=["availability"])