"""Private messaging schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .common import ORMBaseSchema


class MessageCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    recipient_id: str
    content: str = Field(min_length=1, max_length=4000)


class MessageResponse(ORMBaseSchema):
    id: UUID
    sender_id: UUID
    recipient_id: UUID
    content: str
