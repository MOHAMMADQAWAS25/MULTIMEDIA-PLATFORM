from fastapi import APIRouter

from src.interface.routes import health, works

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(works.router)
