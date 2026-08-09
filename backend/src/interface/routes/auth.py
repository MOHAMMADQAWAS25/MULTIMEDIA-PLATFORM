from fastapi import APIRouter, Depends, status

from src.app.auth_service import AuthService
from src.entities.auth import AuthToken, LoginRequest, RegisterUserRequest, UserRead
from src.interface.dependencies.auth_dependencies import get_auth_service, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: RegisterUserRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRead:
    return await auth_service.register_user(payload)


@router.post("/login", response_model=AuthToken)
async def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthToken:
    return await auth_service.login(payload)


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    return current_user
