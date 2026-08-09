from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from src.app.auth_service import AuthService
from src.app.ports import PasswordHasher, TokenIssuer, UserRepository
from src.entities.auth import LoginRequest, RegisterUserRequest, UserRead
from src.entities.exceptions import InvalidCredentialsError, UserAlreadyExistsError


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self.users_by_email: dict[str, UserRead] = {}
        self.password_hashes_by_email: dict[str, str] = {}

    async def get_by_id(self, user_id: UUID) -> UserRead | None:
        return next((user for user in self.users_by_email.values() if user.id == user_id), None)

    async def get_by_email(self, email: str) -> UserRead | None:
        return self.users_by_email.get(email.lower())

    async def get_password_hash_by_email(self, email: str) -> str | None:
        return self.password_hashes_by_email.get(email.lower())

    async def create(self, payload: RegisterUserRequest, password_hash: str) -> UserRead:
        now = datetime.now(UTC)
        user = UserRead(
            id=uuid4(),
            full_name=payload.full_name,
            email=payload.email,
            department=payload.department,
            major=payload.major,
            bio=None,
            profile_photo_url=None,
            role="student",
            is_active=True,
            is_verified=False,
            created_at=now,
            updated_at=now,
        )
        self.users_by_email[str(payload.email).lower()] = user
        self.password_hashes_by_email[str(payload.email).lower()] = password_hash
        return user


class FakePasswordHasher(PasswordHasher):
    def hash_password(self, password: str) -> str:
        return f"hashed:{password}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        return password_hash == f"hashed:{password}"


class FakeTokenIssuer(TokenIssuer):
    def create_access_token(self, subject: UUID) -> tuple[str, datetime]:
        return f"token:{subject}", datetime.now(UTC) + timedelta(minutes=60)

    def verify_access_token(self, token: str) -> UUID:
        return UUID(token.removeprefix("token:"))


@pytest.mark.asyncio
async def test_register_and_login_user() -> None:
    service = AuthService(FakeUserRepository(), FakePasswordHasher(), FakeTokenIssuer())

    user = await service.register_user(
        RegisterUserRequest(
            full_name="Mohammad Qawas",
            email="Mohammad@example.com",
            password="StrongPass123",
            confirm_password="StrongPass123",
            department="Information Technology",
            major="Software Engineering",
        )
    )
    token = await service.login(LoginRequest(email="mohammad@example.com", password="StrongPass123"))

    assert user.email == "Mohammad@example.com"
    assert token.user.id == user.id
    assert token.access_token == f"token:{user.id}"


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email() -> None:
    service = AuthService(FakeUserRepository(), FakePasswordHasher(), FakeTokenIssuer())
    payload = RegisterUserRequest(
        full_name="Mohammad Qawas",
        email="mohammad@example.com",
        password="StrongPass123",
        confirm_password="StrongPass123",
    )

    await service.register_user(payload)

    with pytest.raises(UserAlreadyExistsError):
        await service.register_user(payload)


@pytest.mark.asyncio
async def test_login_rejects_wrong_password() -> None:
    service = AuthService(FakeUserRepository(), FakePasswordHasher(), FakeTokenIssuer())
    await service.register_user(
        RegisterUserRequest(
            full_name="Mohammad Qawas",
            email="mohammad@example.com",
            password="StrongPass123",
            confirm_password="StrongPass123",
        )
    )

    with pytest.raises(InvalidCredentialsError):
        await service.login(LoginRequest(email="mohammad@example.com", password="wrong-password"))
