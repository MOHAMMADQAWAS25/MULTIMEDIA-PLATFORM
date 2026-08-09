from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


def is_allowed_hebron_email(email: str) -> bool:
    normalized = email.lower()
    local_part, _, domain = normalized.partition("@")
    if domain == "students.hebron.edu":
        return local_part.isdecimal()
    if domain == "hebron.edu":
        return bool(local_part)
    return False


class RegisterUserRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)
    department: str | None = Field(default=None, max_length=120)
    major: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def validate_signup_password(self) -> "RegisterUserRequest":
        if not is_allowed_hebron_email(str(self.email)):
            raise ValueError(
                "Email must be a Hebron University email: "
                "[studentnumber]@students.hebron.edu or [name]@hebron.edu."
            )
        if self.password != self.confirm_password:
            raise ValueError("Password confirmation does not match.")
        if not any(character.islower() for character in self.password):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(character.isupper() for character in self.password):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(character.isdigit() for character in self.password):
            raise ValueError("Password must contain at least one number.")
        return self

    def to_user_create(self) -> "UserCreate":
        return UserCreate(
            full_name=self.full_name,
            email=self.email,
            department=self.department,
            major=self.major,
        )


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    department: str | None = Field(default=None, max_length=120)
    major: str | None = Field(default=None, max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    department: str | None
    major: str | None
    bio: str | None
    profile_photo_url: str | None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class SignupStarted(BaseModel):
    email: EmailStr
    expires_at: datetime
    message: str


class VerifySignupRequest(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^\d{6}$")


class SignupVerificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    password_hash: str
    department: str | None
    major: str | None
    code_hash: str
    expires_at: datetime
    consumed_at: datetime | None

    def to_user_create(self) -> UserCreate:
        return UserCreate(
            full_name=self.full_name,
            email=self.email,
            department=self.department,
            major=self.major,
        )


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserRead


class TokenSubject(BaseModel):
    user_id: UUID
