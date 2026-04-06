"""Course announcement router endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from fahimni.core.dependencies import get_current_user, require_role
from fahimni.db.repositories.announcement_repository import AnnouncementRepository
from fahimni.db.session import get_db
from fahimni.models.user import User, UserRole
from fahimni.schemas.announcement import AnnouncementCreate, AnnouncementResponse

router = APIRouter(prefix="/announcements", tags=["announcements"])


@router.post("", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    payload: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PROFESSOR, UserRole.ADMIN)),
) -> AnnouncementResponse:
    repository = AnnouncementRepository(db)
    try:
        announcement = await repository.create_announcement(
            course_id=uuid.UUID(payload.course_id),
            author_id=current_user.id,
            title=payload.title,
            body=payload.body,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid course id") from exc
    return AnnouncementResponse.model_validate(announcement)


@router.get("/course/{course_id}", response_model=list[AnnouncementResponse])
async def list_course_announcements(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[AnnouncementResponse]:
    repository = AnnouncementRepository(db)
    try:
        items = await repository.list_by_course(uuid.UUID(course_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid course id") from exc
    return [AnnouncementResponse.model_validate(item) for item in items]
