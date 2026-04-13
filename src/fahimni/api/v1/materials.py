"""Course material lifecycle and archive router endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from fahimni.core.dependencies import get_current_user
from fahimni.db.repositories.material_repository import MaterialRepository
from fahimni.db.session import get_db
from fahimni.models.course_material import MaterialSourceType, MaterialType
from fahimni.models.learning_event import LearningEventType
from fahimni.models.user import User, UserRole
from fahimni.schemas.material import (
    ArchiveResourceCreate,
    ArchiveResourceResponse,
    CourseMaterialCreate,
    CourseMaterialResponse,
    EventTrackRequest,
    UserProgressResponse,
    UserProgressUpsertRequest,
)

router = APIRouter(prefix="/materials", tags=["materials"])


def _parse_uuid(value: str, label: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {label}") from exc


@router.post("/archive", response_model=ArchiveResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_archive_resource(
    payload: ArchiveResourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ArchiveResourceResponse:
    repository = MaterialRepository(db)
    course_id = _parse_uuid(payload.course_id, "course id")

    is_verified = current_user.role in {UserRole.PROFESSOR, UserRole.ADMIN}
    material = await repository.create_material(
        course_id=course_id,
        title=payload.title,
        material_type=MaterialType.ARCHIVE,
        source_type=MaterialSourceType.ARCHIVE,
        year=payload.year,
        is_verified=is_verified,
        storage_url=payload.file_url,
        created_by=current_user.id,
    )

    archive = await repository.create_archive_resource(
        course_id=course_id,
        title=payload.title,
        resource_type=payload.resource_type,
        year=payload.year,
        university=payload.university,
        professor=payload.professor,
        difficulty=payload.difficulty,
        file_url=payload.file_url,
        material_id=material.id,
        created_by=current_user.id,
    )
    await repository.track_event(
        user_id=current_user.id,
        course_id=course_id,
        event_type=LearningEventType.MATERIAL_UPLOADED,
        topic=payload.title,
        payload={"resource_type": payload.resource_type.value, "year": payload.year},
    )
    return ArchiveResourceResponse.model_validate(archive)


@router.get("/archive/{course_id}", response_model=list[ArchiveResourceResponse])
async def list_archive_resources(
    course_id: str,
    year: int | None = Query(default=None, ge=1990, le=2100),
    only_processed: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ArchiveResourceResponse]:
    repository = MaterialRepository(db)
    parsed_course_id = _parse_uuid(course_id, "course id")

    # Students only see processed archive items until moderation is complete.
    if current_user.role == UserRole.STUDENT:
        only_processed = True

    resources = await repository.list_archive_resources(
        course_id=parsed_course_id,
        year=year,
        only_processed=only_processed,
    )
    return [ArchiveResourceResponse.model_validate(item) for item in resources]


@router.post("", response_model=CourseMaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_material(
    payload: CourseMaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CourseMaterialResponse:
    if current_user.role not in {UserRole.PROFESSOR, UserRole.ADMIN}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teacher/admin can upload official materials")

    repository = MaterialRepository(db)
    course_id = _parse_uuid(payload.course_id, "course id")
    material = await repository.create_material(
        course_id=course_id,
        title=payload.title,
        material_type=payload.material_type,
        source_type=payload.source_type,
        year=payload.year,
        is_verified=True if payload.source_type == MaterialSourceType.TEACHER else payload.is_verified,
        storage_url=payload.storage_url,
        created_by=current_user.id,
    )
    return CourseMaterialResponse.model_validate(material)


@router.get("/{course_id}", response_model=list[CourseMaterialResponse])
async def list_materials(
    course_id: str,
    include_unverified: bool = False,
    source_type: MaterialSourceType | None = None,
    year: int | None = Query(default=None, ge=1990, le=2100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CourseMaterialResponse]:
    repository = MaterialRepository(db)
    parsed_course_id = _parse_uuid(course_id, "course id")

    if current_user.role == UserRole.STUDENT:
        include_unverified = False

    materials = await repository.list_materials(
        course_id=parsed_course_id,
        include_unverified=include_unverified,
        source_type=source_type,
        year=year,
    )
    return [CourseMaterialResponse.model_validate(item) for item in materials]


@router.post("/events", status_code=status.HTTP_201_CREATED)
async def track_event(
    payload: EventTrackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    repository = MaterialRepository(db)
    course_id = _parse_uuid(payload.course_id, "course id")
    event = await repository.track_event(
        user_id=current_user.id,
        course_id=course_id,
        event_type=payload.event_type,
        topic=payload.topic,
        payload=payload.payload,
    )
    return {"event_id": str(event.id)}


@router.post("/progress", response_model=UserProgressResponse, status_code=status.HTTP_201_CREATED)
async def upsert_progress(
    payload: UserProgressUpsertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserProgressResponse:
    repository = MaterialRepository(db)
    course_id = _parse_uuid(payload.course_id, "course id")
    progress = await repository.upsert_progress(
        user_id=current_user.id,
        course_id=course_id,
        topic=payload.topic,
        mastery_score=payload.mastery_score,
        last_seen=payload.last_seen,
    )
    return UserProgressResponse.model_validate(progress)


@router.get("/progress/{course_id}", response_model=list[UserProgressResponse])
async def list_my_progress(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserProgressResponse]:
    repository = MaterialRepository(db)
    parsed_course_id = _parse_uuid(course_id, "course id")
    progress_rows = await repository.list_progress_for_user(
        user_id=current_user.id,
        course_id=parsed_course_id,
    )
    return [UserProgressResponse.model_validate(item) for item in progress_rows]