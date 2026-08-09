from abc import ABC, abstractmethod
from uuid import UUID

from src.entities.auth import RegisterUserRequest, UserRead
from src.entities.work import WorkCreate, WorkRead, WorkStatus


class WorkRepository(ABC):
    @abstractmethod
    async def list_public(self) -> list[WorkRead]:
        raise NotImplementedError

    @abstractmethod
    async def list_pending(self) -> list[WorkRead]:
        raise NotImplementedError

    @abstractmethod
    async def get(self, work_id: UUID) -> WorkRead | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, payload: WorkCreate) -> WorkRead:
        raise NotImplementedError

    @abstractmethod
    async def update_status(self, work_id: UUID, status: WorkStatus) -> WorkRead | None:
        raise NotImplementedError


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> UserRead | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> UserRead | None:
        raise NotImplementedError

    @abstractmethod
    async def get_password_hash_by_email(self, email: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, payload: RegisterUserRequest, password_hash: str) -> UserRead:
        raise NotImplementedError


class PasswordHasher(ABC):
    @abstractmethod
    def hash_password(self, password: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify_password(self, password: str, password_hash: str) -> bool:
        raise NotImplementedError


class TokenIssuer(ABC):
    @abstractmethod
    def create_access_token(self, subject: UUID) -> tuple[str, object]:
        raise NotImplementedError

    @abstractmethod
    def verify_access_token(self, token: str) -> UUID:
        raise NotImplementedError
