from uuid import UUID

from src.app.ports import WorkRepository
from src.entities.exceptions import WorkNotFoundError
from src.entities.work import WorkCreate, WorkRead, WorkStatus


class WorkService:
    def __init__(self, repository: WorkRepository) -> None:
        self.repository = repository

    async def list_public_works(self) -> list[WorkRead]:
        return await self.repository.list_public()

    async def list_pending_works(self) -> list[WorkRead]:
        return await self.repository.list_pending()

    async def get_public_work(self, work_id: UUID) -> WorkRead:
        work = await self.repository.get(work_id)
        if work is None or work.status != WorkStatus.APPROVED:
            raise WorkNotFoundError("Work was not found.")
        return work

    async def submit_work(self, payload: WorkCreate) -> WorkRead:
        return await self.repository.create(payload)

    async def approve_work(self, work_id: UUID) -> WorkRead:
        work = await self.repository.update_status(work_id, WorkStatus.APPROVED)
        if work is None:
            raise WorkNotFoundError("Work was not found.")
        return work

    async def reject_work(self, work_id: UUID) -> WorkRead:
        work = await self.repository.update_status(work_id, WorkStatus.REJECTED)
        if work is None:
            raise WorkNotFoundError("Work was not found.")
        return work
