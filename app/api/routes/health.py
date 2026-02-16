from fastapi import APIRouter
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.db_check import router as db_check_router

router = APIRouter()

router.include_router(health_router, tags=["health_router"])
router.include_router(db_check_router, tags=["db_check_router"])