from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.app.work_service import WorkService
from src.entities.categories import WorkCategory
from src.entities.work import WorkCreate, WorkModerationRequest, WorkRead
from src.interface.dependencies.work_dependencies import get_work_service

router = APIRouter(prefix="/works", tags=["works"])


@router.get("/categories")
def list_work_categories() -> list[dict[str, str]]:
    return [{"value": category.value, "label": category.name.replace("_", " ").title()} for category in WorkCategory]


@router.get("", response_model=list[WorkRead])
def list_public_works(service: WorkService = Depends(get_work_service)) -> list[WorkRead]:
    return service.list_public_works()


@router.post("", response_model=WorkRead, status_code=status.HTTP_201_CREATED)
def submit_work(
    payload: WorkCreate,
    service: WorkService = Depends(get_work_service),
) -> WorkRead:
    return service.submit_work(payload)


@router.get("/moderation/pending", response_model=list[WorkRead])
def list_pending_works(service: WorkService = Depends(get_work_service)) -> list[WorkRead]:
    return service.list_pending_works()


@router.get("/{work_id}", response_model=WorkRead)
def get_public_work(
    work_id: UUID,
    service: WorkService = Depends(get_work_service),
) -> WorkRead:
    return service.get_public_work(work_id)


@router.post("/{work_id}/approve", response_model=WorkRead)
def approve_work(
    work_id: UUID,
    _: WorkModerationRequest | None = None,
    service: WorkService = Depends(get_work_service),
) -> WorkRead:
    return service.approve_work(work_id)


@router.post("/{work_id}/reject", response_model=WorkRead)
def reject_work(
    work_id: UUID,
    _: WorkModerationRequest | None = None,
    service: WorkService = Depends(get_work_service),
) -> WorkRead:
    return service.reject_work(work_id)
