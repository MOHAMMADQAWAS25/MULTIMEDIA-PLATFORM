from functools import lru_cache

from src.app.work_service import WorkService
from src.infrastructure.repositories.in_memory_work_repository import InMemoryWorkRepository


@lru_cache
def get_work_repository() -> InMemoryWorkRepository:
    return InMemoryWorkRepository()


def get_work_service() -> WorkService:
    return WorkService(get_work_repository())
