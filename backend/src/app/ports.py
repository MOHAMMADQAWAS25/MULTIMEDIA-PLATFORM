from abc import ABC, abstractmethod
from uuid import UUID

from src.entities.work import WorkCreate, WorkRead, WorkStatus


class WorkRepository(ABC):
    @abstractmethod
    def list_public(self) -> list[WorkRead]:
        raise NotImplementedError

    @abstractmethod
    def list_pending(self) -> list[WorkRead]:
        raise NotImplementedError

    @abstractmethod
    def get(self, work_id: UUID) -> WorkRead | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, payload: WorkCreate) -> WorkRead:
        raise NotImplementedError

    @abstractmethod
    def update_status(self, work_id: UUID, status: WorkStatus) -> WorkRead | None:
        raise NotImplementedError
