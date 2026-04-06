"""Repository for user persistence operations."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fahimni.models.user import User, UserRole


class UserRepository:
    """Data access layer for user entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_user(
        self,
        *,
        email: str,
        hashed_password: str,
        full_name: str,
        role: UserRole,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=True,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def list_users(self) -> list[User]:
        result = await self.db.execute(select(User).order_by(User.created_at.desc()))
        return list(result.scalars().all())
