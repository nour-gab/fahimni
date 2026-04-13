"""Schemas for AI assistant, OCR, search, and analytics workflows."""

from pydantic import BaseModel, ConfigDict, Field


class AskRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    course_id: str
    question: str = Field(min_length=2)
    task_hint: str = ""


class SearchRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    course_id: str
    query: str = Field(min_length=2)
    k: int = Field(default=5, ge=1, le=20)


class TeacherAssistRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    course_id: str
    content: str = Field(min_length=10)


class MultiAgentRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    course_id: str
    student_id: str
    prompt: str = Field(min_length=2)


class LearningPathRequest(BaseModel):
    weak_topics: list[str]
    study_minutes_per_day: int = Field(default=60, ge=15, le=300)
    horizon_days: int = Field(default=7, ge=1, le=30)


class ExamGeneratorRequest(BaseModel):
    course_id: str
    topic: str
    question_count: int = Field(default=5, ge=1, le=30)


class AnswerCorrectionRequest(BaseModel):
    reference_answer: str
    student_answer: str


class AnalyticsRequest(BaseModel):
    records: list[dict[str, object]]
