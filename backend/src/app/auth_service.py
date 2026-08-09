from uuid import UUID

from src.app.ports import PasswordHasher, TokenIssuer, UserRepository
from src.entities.auth import AuthToken, LoginRequest, RegisterUserRequest, UserRead
from src.entities.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    UnauthorizedError,
    UserAlreadyExistsError,
)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_issuer: TokenIssuer,
    ) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_issuer = token_issuer

    async def register_user(self, payload: RegisterUserRequest) -> UserRead:
        existing = await self.user_repository.get_by_email(str(payload.email).lower())
        if existing is not None:
            raise UserAlreadyExistsError("A user with this email already exists.")

        password_hash = self.password_hasher.hash_password(payload.password)
        return await self.user_repository.create(payload, password_hash)

    async def login(self, payload: LoginRequest) -> AuthToken:
        email = str(payload.email).lower()
        user = await self.user_repository.get_by_email(email)
        password_hash = await self.user_repository.get_password_hash_by_email(email)

        if user is None or password_hash is None:
            raise InvalidCredentialsError("Email or password is incorrect.")
        if not self.password_hasher.verify_password(payload.password, password_hash):
            raise InvalidCredentialsError("Email or password is incorrect.")
        if not user.is_active:
            raise InactiveUserError("This user account is inactive.")

        token, expires_at = self.token_issuer.create_access_token(user.id)
        return AuthToken(access_token=token, expires_at=expires_at, user=user)

    async def get_current_user(self, user_id: UUID) -> UserRead:
        user = await self.user_repository.get_by_id(user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("Authentication is required.")
        return user
