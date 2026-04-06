"""Private messaging router endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from fahimni.core.dependencies import get_current_user
from fahimni.db.repositories.message_repository import MessageRepository
from fahimni.db.session import get_db
from fahimni.models.user import User
from fahimni.schemas.message import MessageCreate, MessageResponse

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    repository = MessageRepository(db)
    try:
        message = await repository.create_message(
            sender_id=current_user.id,
            recipient_id=uuid.UUID(payload.recipient_id),
            content=payload.content,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid recipient id") from exc
    return MessageResponse.model_validate(message)


@router.get("/conversation/{other_user_id}", response_model=list[MessageResponse])
async def get_conversation(
    other_user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MessageResponse]:
    repository = MessageRepository(db)
    try:
        messages = await repository.list_conversation(current_user.id, uuid.UUID(other_user_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid other user id") from exc
    return [MessageResponse.model_validate(item) for item in messages]
