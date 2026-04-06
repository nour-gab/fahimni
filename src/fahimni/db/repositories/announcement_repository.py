"""Repository for course announcement persistence."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fahimni.models.announcement import Announcement


class AnnouncementRepository:
    """Data access layer for announcement entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_announcement(
        self,
        *,
        course_id: uuid.UUID,
        author_id: uuid.UUID,
        title: str,
        body: str,
    ) -> Announcement:
        announcement = Announcement(
            course_id=course_id,
            author_id=author_id,
            title=title,
            body=body,
        )
        self.db.add(announcement)
        await self.db.flush()
        await self.db.refresh(announcement)
        return announcement

    async def list_by_course(self, course_id: uuid.UUID) -> list[Announcement]:
        result = await self.db.execute(
            select(Announcement)
            .where(Announcement.course_id == course_id)
            .order_by(Announcement.created_at.desc())
        )
        return list(result.scalars().all())
