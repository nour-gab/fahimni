"""Repository for course materials, archive resources, progress, and events."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fahimni.models.archive_resource import (
    ArchiveDifficulty,
    ArchiveResource,
    ArchiveResourceType,
)
from fahimni.models.course_material import CourseMaterial, MaterialSourceType, MaterialType
from fahimni.models.learning_event import LearningEvent, LearningEventType
from fahimni.models.user_progress import UserProgress


class MaterialRepository:
    """Data access layer for the knowledge lifecycle and archive features."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_material(
        self,
        *,
        course_id: uuid.UUID,
        title: str,
        material_type: MaterialType,
        source_type: MaterialSourceType,
        year: int,
        is_verified: bool,
        storage_url: str,
        created_by: uuid.UUID,
    ) -> CourseMaterial:
        material = CourseMaterial(
            course_id=course_id,
            title=title,
            material_type=material_type,
            source_type=source_type,
            year=year,
            is_verified=is_verified,
            storage_url=storage_url,
            created_by=created_by,
        )
        self.db.add(material)
        await self.db.flush()
        await self.db.refresh(material)
        return material

    async def list_materials(
        self,
        *,
        course_id: uuid.UUID,
        include_unverified: bool = False,
        source_type: MaterialSourceType | None = None,
        year: int | None = None,
    ) -> list[CourseMaterial]:
        query = select(CourseMaterial).where(CourseMaterial.course_id == course_id)
        if not include_unverified:
            query = query.where(CourseMaterial.is_verified.is_(True))
        if source_type is not None:
            query = query.where(CourseMaterial.source_type == source_type)
        if year is not None:
            query = query.where(CourseMaterial.year == year)
        query = query.order_by(CourseMaterial.year.desc(), CourseMaterial.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_archive_resource(
        self,
        *,
        course_id: uuid.UUID,
        title: str,
        resource_type: ArchiveResourceType,
        year: int,
        university: str,
        professor: str | None,
        difficulty: ArchiveDifficulty,
        file_url: str,
        material_id: uuid.UUID | None,
        created_by: uuid.UUID,
    ) -> ArchiveResource:
        item = ArchiveResource(
            course_id=course_id,
            material_id=material_id,
            title=title,
            resource_type=resource_type,
            year=year,
            university=university,
            professor=professor,
            difficulty=difficulty,
            file_url=file_url,
            created_by=created_by,
        )
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def list_archive_resources(
        self,
        *,
        course_id: uuid.UUID,
        year: int | None = None,
        only_processed: bool = False,
    ) -> list[ArchiveResource]:
        query = select(ArchiveResource).where(ArchiveResource.course_id == course_id)
        if year is not None:
            query = query.where(ArchiveResource.year == year)
        if only_processed:
            query = query.where(ArchiveResource.processed.is_(True))
        query = query.order_by(ArchiveResource.year.desc(), ArchiveResource.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_archive_processed(self, archive_id: uuid.UUID, processed: bool = True) -> ArchiveResource | None:
        result = await self.db.execute(
            select(ArchiveResource).where(ArchiveResource.id == archive_id)
        )
        item = result.scalar_one_or_none()
        if item is None:
            return None
        item.processed = processed
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def track_event(
        self,
        *,
        user_id: uuid.UUID,
        course_id: uuid.UUID,
        event_type: LearningEventType,
        topic: str | None,
        payload: dict[str, object],
    ) -> LearningEvent:
        event = LearningEvent(
            user_id=user_id,
            course_id=course_id,
            event_type=event_type,
            topic=topic,
            payload=payload,
        )
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def upsert_progress(
        self,
        *,
        user_id: uuid.UUID,
        course_id: uuid.UUID,
        topic: str,
        mastery_score: float,
        last_seen: datetime | None = None,
    ) -> UserProgress:
        timestamp = last_seen or datetime.now(UTC)
        result = await self.db.execute(
            select(UserProgress).where(
                UserProgress.user_id == user_id,
                UserProgress.course_id == course_id,
                UserProgress.topic == topic,
            )
        )
        progress = result.scalar_one_or_none()
        if progress is None:
            progress = UserProgress(
                user_id=user_id,
                course_id=course_id,
                topic=topic,
                mastery_score=mastery_score,
                last_seen=timestamp,
            )
            self.db.add(progress)
        else:
            progress.mastery_score = mastery_score
            progress.last_seen = timestamp

        await self.db.flush()
        await self.db.refresh(progress)
        return progress

    async def list_progress_for_user(
        self,
        *,
        user_id: uuid.UUID,
        course_id: uuid.UUID,
    ) -> list[UserProgress]:
        result = await self.db.execute(
            select(UserProgress)
            .where(
                UserProgress.user_id == user_id,
                UserProgress.course_id == course_id,
            )
            .order_by(UserProgress.updated_at.desc())
        )
        return list(result.scalars().all())