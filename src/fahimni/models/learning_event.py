"""Event log model for AI, quiz, and study interaction telemetry."""

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum as SAEnum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from fahimni.db.base import Base


class LearningEventType(enum.StrEnum):
    QUESTION_ASKED = "QUESTION_ASKED"
    QUIZ_TAKEN = "QUIZ_TAKEN"
    MISTAKE_RECORDED = "MISTAKE_RECORDED"
    MATERIAL_UPLOADED = "MATERIAL_UPLOADED"


class LearningEvent(Base):
    __tablename__ = "learning_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[LearningEventType] = mapped_column(SAEnum(LearningEventType), nullable=False)
    topic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())