"""Repository for private user-to-user messages."""

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from fahimni.models.message import Message


class MessageRepository:
    """Data access layer for direct message entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_message(self, *, sender_id: uuid.UUID, recipient_id: uuid.UUID, content: str) -> Message:
        message = Message(sender_id=sender_id, recipient_id=recipient_id, content=content)
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def list_conversation(self, user_a: uuid.UUID, user_b: uuid.UUID) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(
                or_(
                    (Message.sender_id == user_a) & (Message.recipient_id == user_b),
                    (Message.sender_id == user_b) & (Message.recipient_id == user_a),
                )
            )
            .order_by(Message.sent_at.asc())
        )
        return list(result.scalars().all())
