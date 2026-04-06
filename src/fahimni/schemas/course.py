"""Course and enrollment schemas."""

from pydantic import BaseModel, ConfigDict, Field

from .common import ORMBaseSchema


class CourseCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=255)
    code: str = Field(min_length=2, max_length=30)
    description: str = Field(default="", max_length=1000)


class CourseResponse(ORMBaseSchema):
    id: str
    title: str
    code: str
    description: str
    professor_id: str


class EnrollmentCreate(BaseModel):
    course_id: str
    student_id: str
