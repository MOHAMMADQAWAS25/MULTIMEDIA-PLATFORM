from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.entities.exceptions import InkFigError, WorkNotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(WorkNotFoundError)
    async def work_not_found_handler(_: Request, exc: WorkNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(InkFigError)
    async def inkfig_error_handler(_: Request, exc: InkFigError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": exc.code, "message": exc.message}},
        )
