"""Announcement schemas for course-wide communication."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .common import ORMBaseSchema


class AnnouncementCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    course_id: str
    title: str = Field(min_length=3, max_length=255)
    body: str = Field(min_length=1)


class AnnouncementResponse(ORMBaseSchema):
    id: UUID
    course_id: UUID
    author_id: UUID
    title: str
    body: str
