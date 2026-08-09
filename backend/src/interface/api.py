from fastapi import APIRouter

from src.interface.routes import auth, health, works

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(health.router)
api_router.include_router(works.router)
