from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.app.ports import (
    EmailSender,
    PasswordHasher,
    SignupVerificationRepository,
    TokenIssuer,
    UserRepository,
    VerificationCodeGenerator,
    VerificationCodeHasher,
)
from src.entities.auth import (
    AuthToken,
    LoginRequest,
    RegisterUserRequest,
    SignupStarted,
    UserRead,
    VerifySignupRequest,
)
from src.entities.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    SignupVerificationError,
    UnauthorizedError,
    UserAlreadyExistsError,
)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        signup_verification_repository: SignupVerificationRepository,
        password_hasher: PasswordHasher,
        code_hasher: VerificationCodeHasher,
        code_generator: VerificationCodeGenerator,
        email_sender: EmailSender,
        token_issuer: TokenIssuer,
        signup_code_expire_minutes: int,
    ) -> None:
        self.user_repository = user_repository
        self.signup_verification_repository = signup_verification_repository
        self.password_hasher = password_hasher
        self.code_hasher = code_hasher
        self.code_generator = code_generator
        self.email_sender = email_sender
        self.token_issuer = token_issuer
        self.signup_code_expire_minutes = signup_code_expire_minutes

    async def start_signup(self, payload: RegisterUserRequest) -> SignupStarted:
        existing = await self.user_repository.get_by_email(str(payload.email).lower())
        if existing is not None:
            raise UserAlreadyExistsError("A user with this email already exists.")

        password_hash = self.password_hasher.hash_password(payload.password)
        code = self.code_generator.generate_code()
        code_hash = self.code_hasher.hash_code(str(payload.email), code)
        expires_at = datetime.now(UTC) + timedelta(minutes=self.signup_code_expire_minutes)
        await self.signup_verification_repository.upsert_request(
            payload,
            password_hash,
            code_hash,
            expires_at,
        )
        await self.email_sender.send_signup_verification_code(str(payload.email), code)
        return SignupStarted(
            email=payload.email,
            expires_at=expires_at,
            message="Verification code sent to email.",
        )

    async def verify_signup(self, payload: VerifySignupRequest) -> UserRead:
        email = str(payload.email).lower()
        existing = await self.user_repository.get_by_email(email)
        if existing is not None:
            raise UserAlreadyExistsError("A user with this email already exists.")

        verification = await self.signup_verification_repository.get_valid_request(
            email,
            datetime.now(UTC),
        )
        if verification is None:
            raise SignupVerificationError("Verification code is invalid or expired.")
        if not self.code_hasher.verify_code(email, payload.code, verification.code_hash):
            raise SignupVerificationError("Verification code is invalid or expired.")

        user = await self.user_repository.create(
            verification.to_user_create(),
            verification.password_hash,
        )
        await self.signup_verification_repository.mark_consumed(verification.id)
        return user

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
