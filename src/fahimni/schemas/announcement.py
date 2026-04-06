"""Announcement schemas for course-wide communication."""

from pydantic import BaseModel, ConfigDict, Field

from .common import ORMBaseSchema


class AnnouncementCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    course_id: str
    title: str = Field(min_length=3, max_length=255)
    body: str = Field(min_length=1)


class AnnouncementResponse(ORMBaseSchema):
    id: str
    course_id: str
    author_id: str
    title: str
    body: str
