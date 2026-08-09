from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.ports import UserRepository
from src.entities.auth import RegisterUserRequest, UserRead
from src.infrastructure.models.user import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> UserRead | None:
        user = await self.session.get(UserModel, user_id)
        return self._to_read(user) if user is not None else None

    async def get_by_email(self, email: str) -> UserRead | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email.lower())
        )
        user = result.scalar_one_or_none()
        return self._to_read(user) if user is not None else None

    async def get_password_hash_by_email(self, email: str) -> str | None:
        result = await self.session.execute(
            select(UserModel.password_hash).where(UserModel.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def create(self, payload: RegisterUserRequest, password_hash: str) -> UserRead:
        user = UserModel(
            full_name=payload.full_name,
            email=str(payload.email).lower(),
            password_hash=password_hash,
            department=payload.department,
            major=payload.major,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return self._to_read(user)

    def _to_read(self, user: UserModel) -> UserRead:
        return UserRead.model_validate(user)
