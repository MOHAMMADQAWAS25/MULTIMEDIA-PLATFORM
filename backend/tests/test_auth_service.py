from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from src.app.auth_service import AuthService
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
    LoginRequest,
    RegisterUserRequest,
    SignupVerificationRead,
    UserCreate,
    UserRead,
    VerifySignupRequest,
    is_allowed_hebron_email,
)
from src.entities.exceptions import (
    InvalidCredentialsError,
    SignupVerificationError,
    UserAlreadyExistsError,
)


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

    async def create(self, payload: UserCreate, password_hash: str) -> UserRead:
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


class FakeSignupVerificationRepository(SignupVerificationRepository):
    def __init__(self) -> None:
        self.request: SignupVerificationRead | None = None

    async def upsert_request(
        self,
        payload: RegisterUserRequest,
        password_hash: str,
        code_hash: str,
        expires_at: datetime,
    ) -> None:
        self.request = SignupVerificationRead(
            id=uuid4(),
            full_name=payload.full_name,
            email=payload.email,
            password_hash=password_hash,
            department=payload.department,
            major=payload.major,
            code_hash=code_hash,
            expires_at=expires_at,
            consumed_at=None,
        )

    async def get_valid_request(self, email: str, now: datetime) -> SignupVerificationRead | None:
        if self.request is None:
            return None
        if str(self.request.email).lower() != email.lower():
            return None
        if self.request.consumed_at is not None or self.request.expires_at <= now:
            return None
        return self.request

    async def mark_consumed(self, verification_id: UUID) -> None:
        if self.request is not None and self.request.id == verification_id:
            self.request = self.request.model_copy(update={"consumed_at": datetime.now(UTC)})


class FakeVerificationCodeHasher(VerificationCodeHasher):
    def hash_code(self, email: str, code: str) -> str:
        return f"{email.lower()}:{code}"

    def verify_code(self, email: str, code: str, code_hash: str) -> bool:
        return code_hash == self.hash_code(email, code)


class FakeVerificationCodeGenerator(VerificationCodeGenerator):
    def generate_code(self) -> str:
        return "123456"


class FakeEmailSender(EmailSender):
    def __init__(self) -> None:
        self.sent_codes: list[tuple[str, str]] = []

    async def send_signup_verification_code(self, email: str, code: str) -> None:
        self.sent_codes.append((email, code))


def create_auth_service() -> tuple[AuthService, FakeEmailSender]:
    email_sender = FakeEmailSender()
    service = AuthService(
        FakeUserRepository(),
        FakeSignupVerificationRepository(),
        FakePasswordHasher(),
        FakeVerificationCodeHasher(),
        FakeVerificationCodeGenerator(),
        email_sender,
        FakeTokenIssuer(),
        signup_code_expire_minutes=10,
    )
    return service, email_sender


@pytest.mark.asyncio
async def test_register_and_login_user() -> None:
    service, email_sender = create_auth_service()

    started = await service.start_signup(
        RegisterUserRequest(
            full_name="Mohammad Qawas",
            email="202012345@STUDENTS.HEBRON.EDU",
            password="StrongPass123",
            confirm_password="StrongPass123",
            department="Information Technology",
            major="Software Engineering",
        )
    )
    user = await service.verify_signup(
        VerifySignupRequest(email="202012345@students.hebron.edu", code="123456")
    )
    token = await service.login(
        LoginRequest(email="202012345@students.hebron.edu", password="StrongPass123")
    )

    assert started.message == "Verification code sent to email."
    assert email_sender.sent_codes == [("202012345@students.hebron.edu", "123456")]
    assert str(user.email) == "202012345@students.hebron.edu"
    assert token.user.id == user.id
    assert token.access_token == f"token:{user.id}"


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email() -> None:
    service, _ = create_auth_service()
    payload = RegisterUserRequest(
        full_name="Mohammad Qawas",
        email="mohammad@hebron.edu",
        password="StrongPass123",
        confirm_password="StrongPass123",
    )

    await service.start_signup(payload)
    await service.verify_signup(VerifySignupRequest(email="mohammad@hebron.edu", code="123456"))

    with pytest.raises(UserAlreadyExistsError):
        await service.start_signup(payload)


@pytest.mark.asyncio
async def test_login_rejects_wrong_password() -> None:
    service, _ = create_auth_service()
    await service.start_signup(
        RegisterUserRequest(
            full_name="Mohammad Qawas",
            email="mohammad@hebron.edu",
            password="StrongPass123",
            confirm_password="StrongPass123",
        )
    )
    await service.verify_signup(VerifySignupRequest(email="mohammad@hebron.edu", code="123456"))

    with pytest.raises(InvalidCredentialsError):
        await service.login(LoginRequest(email="mohammad@hebron.edu", password="wrong-password"))


@pytest.mark.asyncio
async def test_verify_signup_rejects_wrong_code() -> None:
    service, _ = create_auth_service()
    await service.start_signup(
        RegisterUserRequest(
            full_name="Mohammad Qawas",
            email="mohammad@hebron.edu",
            password="StrongPass123",
            confirm_password="StrongPass123",
        )
    )

    with pytest.raises(SignupVerificationError):
        await service.verify_signup(VerifySignupRequest(email="mohammad@hebron.edu", code="000000"))


def test_signup_email_accepts_only_hebron_university_addresses() -> None:
    assert is_allowed_hebron_email("202012345@STUDENTS.HEBRON.EDU")
    assert is_allowed_hebron_email("teacher.name@HEBRON.EDU")
    assert not is_allowed_hebron_email("student.name@students.hebron.edu")
    assert not is_allowed_hebron_email("mohammad@example.com")


def test_signup_rejects_non_hebron_email() -> None:
    with pytest.raises(ValidationError):
        RegisterUserRequest(
            full_name="Mohammad Qawas",
            email="mohammad@example.com",
            password="StrongPass123",
            confirm_password="StrongPass123",
        )
