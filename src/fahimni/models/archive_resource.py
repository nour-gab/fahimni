"""Archive resource model for historical course assets and exam intelligence."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from fahimni.db.base import Base


class ArchiveResourceType(enum.StrEnum):
    EXAM = "EXAM"
    TD = "TD"
    SUMMARY = "SUMMARY"


class ArchiveDifficulty(enum.StrEnum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class ArchiveResource(Base):
    __tablename__ = "archive_resources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    material_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("course_materials.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[ArchiveResourceType] = mapped_column(SAEnum(ArchiveResourceType), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    university: Mapped[str] = mapped_column(String(255), nullable=False)
    professor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    difficulty: Mapped[ArchiveDifficulty] = mapped_column(SAEnum(ArchiveDifficulty), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())