from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.config import settings
from src.interface.api import api_router
from src.interface.exception_handlers import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(
        title="InkFig API",
        version="0.1.0",
        description="Backend API for InkFig, a university digital art portfolio platform.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
