import hmac
import secrets
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import UUID

import jwt
import bcrypt
from jwt import InvalidTokenError

from src.app.ports import PasswordHasher, TokenIssuer, VerificationCodeGenerator, VerificationCodeHasher
from src.entities.exceptions import UnauthorizedError
from src.infrastructure.config import settings


class BcryptPasswordHasher(PasswordHasher):
    def hash_password(self, password: str) -> str:
        password_bytes = password.encode("utf-8")
        return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


class HmacVerificationCodeHasher(VerificationCodeHasher):
    def hash_code(self, email: str, code: str) -> str:
        message = f"{email.lower()}:{code}".encode("utf-8")
        return hmac.new(settings.signup_code_secret.encode("utf-8"), message, sha256).hexdigest()

    def verify_code(self, email: str, code: str, code_hash: str) -> bool:
        expected = self.hash_code(email, code)
        return hmac.compare_digest(expected, code_hash)


class SixDigitVerificationCodeGenerator(VerificationCodeGenerator):
    def generate_code(self) -> str:
        return f"{secrets.randbelow(1_000_000):06d}"


class JwtTokenIssuer(TokenIssuer):
    def create_access_token(self, subject: UUID) -> tuple[str, datetime]:
        expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
        payload = {
            "sub": str(subject),
            "type": "access",
            "exp": expires_at,
            "iat": datetime.now(UTC),
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return token, expires_at

    def verify_access_token(self, token: str) -> UUID:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            if payload.get("type") != "access":
                raise UnauthorizedError("Invalid authentication token.")
            subject = payload.get("sub")
            if not isinstance(subject, str):
                raise UnauthorizedError("Invalid authentication token.")
            return UUID(subject)
        except (InvalidTokenError, ValueError) as exc:
            raise UnauthorizedError("Invalid authentication token.") from exc
