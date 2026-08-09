from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.auth_service import AuthService
from src.entities.auth import UserRead
from src.infrastructure.database import get_db_session
from src.infrastructure.email import SmtpEmailSender
from src.infrastructure.config import settings
from src.infrastructure.repositories.sqlalchemy_signup_verification_repository import (
    SqlAlchemySignupVerificationRepository,
)
from src.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from src.infrastructure.security import (
    BcryptPasswordHasher,
    HmacVerificationCodeHasher,
    JwtTokenIssuer,
    SixDigitVerificationCodeGenerator,
)

bearer_scheme = HTTPBearer(auto_error=False)


def get_password_hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher()


def get_token_issuer() -> JwtTokenIssuer:
    return JwtTokenIssuer()


def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
) -> AuthService:
    return AuthService(
        user_repository=SqlAlchemyUserRepository(session),
        signup_verification_repository=SqlAlchemySignupVerificationRepository(session),
        password_hasher=get_password_hasher(),
        code_hasher=HmacVerificationCodeHasher(),
        code_generator=SixDigitVerificationCodeGenerator(),
        email_sender=SmtpEmailSender(),
        token_issuer=get_token_issuer(),
        signup_code_expire_minutes=settings.signup_code_expire_minutes,
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRead:
    token_issuer = get_token_issuer()
    if credentials is None:
        from src.entities.exceptions import UnauthorizedError

        raise UnauthorizedError("Authentication is required.")
    user_id = token_issuer.verify_access_token(credentials.credentials)
    return await auth_service.get_current_user(user_id)
