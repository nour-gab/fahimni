"""Assignment and grade schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .common import ORMBaseSchema


class AssignmentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    course_id: str
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(default="")
    total_points: float = Field(default=100.0, ge=0.0)


class GradeCreate(BaseModel):
    assignment_id: str
    student_id: str
    score: float = Field(ge=0)
    feedback: str = ""


class AssignmentResponse(ORMBaseSchema):
    id: UUID
    course_id: UUID
    title: str
    description: str
    total_points: float


class GradeResponse(ORMBaseSchema):
    id: UUID
    assignment_id: UUID
    student_id: UUID
    score: float
    feedback: str
