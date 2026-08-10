from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.ports import SignupVerificationRepository
from src.entities.auth import RegisterUserRequest, SignupVerificationRead
from src.infrastructure.models.signup_verification import SignupVerificationModel


class SqlAlchemySignupVerificationRepository(SignupVerificationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_request(
        self,
        payload: RegisterUserRequest,
        password_hash: str,
        code_hash: str,
        expires_at: datetime,
    ) -> None:
        email = str(payload.email).lower()
        await self.session.execute(
            update(SignupVerificationModel)
            .where(
                SignupVerificationModel.email == email,
                SignupVerificationModel.consumed_at.is_(None),
            )
            .values(consumed_at=datetime.now(UTC))
        )
        self.session.add(
            SignupVerificationModel(
                full_name=payload.full_name,
                email=email,
                password_hash=password_hash,
                department=payload.department,
                major=payload.major,
                code_hash=code_hash,
                expires_at=expires_at,
            )
        )
        await self.session.commit()

    async def get_valid_request(
        self,
        email: str,
        now: datetime,
    ) -> SignupVerificationRead | None:
        result = await self.session.execute(
            select(SignupVerificationModel)
            .where(
                SignupVerificationModel.email == email.lower(),
                SignupVerificationModel.consumed_at.is_(None),
                SignupVerificationModel.expires_at > now,
            )
            .order_by(SignupVerificationModel.created_at.desc())
            .limit(1)
        )
        verification = result.scalar_one_or_none()
        return self._to_read(verification) if verification is not None else None

    async def mark_consumed(self, verification_id: UUID) -> None:
        await self.session.execute(
            update(SignupVerificationModel)
            .where(SignupVerificationModel.id == verification_id)
            .values(consumed_at=datetime.now(UTC))
        )
        await self.session.commit()

    def _to_read(self, verification: SignupVerificationModel) -> SignupVerificationRead:
        return SignupVerificationRead.model_validate(verification)
