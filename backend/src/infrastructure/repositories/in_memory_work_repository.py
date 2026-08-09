from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.app.ports import WorkRepository
from src.entities.work import WorkCreate, WorkRead, WorkStatus


class InMemoryWorkRepository(WorkRepository):
    def __init__(self) -> None:
        self._works: dict[UUID, WorkRead] = {}

    def list_public(self) -> list[WorkRead]:
        return [work for work in self._works.values() if work.status == WorkStatus.APPROVED]

    def list_pending(self) -> list[WorkRead]:
        return [work for work in self._works.values() if work.status == WorkStatus.PENDING]

    def get(self, work_id: UUID) -> WorkRead | None:
        return self._works.get(work_id)

    def create(self, payload: WorkCreate) -> WorkRead:
        now = datetime.now(UTC)
        work = WorkRead(
            id=uuid4(),
            title=payload.title,
            description=payload.description,
            category=payload.category,
            owner_id=payload.owner_id,
            tags=payload.tags,
            file_url=payload.file_url,
            thumbnail_url=payload.thumbnail_url,
            downloads_allowed=payload.downloads_allowed,
            status=WorkStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self._works[work.id] = work
        return work

    def update_status(self, work_id: UUID, status: WorkStatus) -> WorkRead | None:
        work = self._works.get(work_id)
        if work is None:
            return None
        updated = work.model_copy(update={"status": status, "updated_at": datetime.now(UTC)})
        self._works[work_id] = updated
        return updated
