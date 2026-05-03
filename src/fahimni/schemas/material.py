"""Schemas for course material lifecycle, archive resources, and learning telemetry."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from fahimni.models.archive_resource import ArchiveDifficulty, ArchiveResourceType
from fahimni.models.course_material import MaterialSourceType, MaterialType
from fahimni.models.learning_event import LearningEventType

from .common import ORMBaseSchema


class CourseMaterialCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    course_id: str
    title: str = Field(min_length=3, max_length=255)
    material_type: MaterialType
    source_type: MaterialSourceType
    year: int = Field(ge=1990, le=2100)
    is_verified: bool = False
    storage_url: str = Field(default="", max_length=1024)


class CourseMaterialResponse(ORMBaseSchema):
    id: UUID
    course_id: UUID
    title: str
    material_type: MaterialType
    source_type: MaterialSourceType
    year: int
    is_verified: bool
    version: int
    is_current: bool
    storage_url: str
    created_by: UUID | None


class ArchiveResourceCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    course_id: str
    title: str = Field(min_length=3, max_length=255)
    resource_type: ArchiveResourceType
    year: int = Field(ge=1990, le=2100)
    university: str = Field(min_length=2, max_length=255)
    professor: str | None = Field(default=None, max_length=255)
    difficulty: ArchiveDifficulty = ArchiveDifficulty.MEDIUM
    file_url: str = Field(min_length=3, max_length=1024)


class ArchiveResourceResponse(ORMBaseSchema):
    id: UUID
    course_id: UUID
    material_id: UUID | None
    title: str
    resource_type: ArchiveResourceType
    year: int
    university: str
    professor: str | None
    difficulty: ArchiveDifficulty
    file_url: str
    processed: bool
    created_by: UUID | None


class EventTrackRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    course_id: str
    event_type: LearningEventType
    topic: str | None = Field(default=None, max_length=255)
    payload: dict[str, object] = Field(default_factory=dict)


class UserProgressUpsertRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    course_id: str
    topic: str = Field(min_length=2, max_length=255)
    mastery_score: float = Field(ge=0, le=100)
    last_seen: datetime | None = None


class UserProgressResponse(ORMBaseSchema):
    id: UUID
    user_id: UUID
    course_id: UUID
    topic: str
    mastery_score: float
    last_seen: datetime