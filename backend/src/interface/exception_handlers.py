from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.entities.exceptions import (
    InactiveUserError,
    InkFigError,
    InvalidCredentialsError,
    UnauthorizedError,
    UserAlreadyExistsError,
    WorkNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(WorkNotFoundError)
    async def work_not_found_handler(_: Request, exc: WorkNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_handler(_: Request, exc: UserAlreadyExistsError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(_: Request, exc: InvalidCredentialsError) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(InactiveUserError)
    async def inactive_user_handler(_: Request, exc: InactiveUserError) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(_: Request, exc: UnauthorizedError) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"error": {"code": exc.code, "message": exc.message}},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(InkFigError)
    async def inkfig_error_handler(_: Request, exc: InkFigError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": exc.code, "message": exc.message}},
        )
