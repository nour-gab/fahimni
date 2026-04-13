"""Course material model for lifecycle, provenance, and verification tracking."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from fahimni.db.base import Base


class MaterialType(enum.StrEnum):
    PDF = "PDF"
    IMAGE = "IMAGE"
    NOTES = "NOTES"
    ARCHIVE = "ARCHIVE"


class MaterialSourceType(enum.StrEnum):
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    ARCHIVE = "ARCHIVE"


class CourseMaterial(Base):
    __tablename__ = "course_materials"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    material_type: Mapped[MaterialType] = mapped_column(SAEnum(MaterialType), nullable=False)
    source_type: Mapped[MaterialSourceType] = mapped_column(SAEnum(MaterialSourceType), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    storage_url: Mapped[str] = mapped_column(String(1024), default="")
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )