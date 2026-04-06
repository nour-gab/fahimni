"""Declarative base for all SQLAlchemy ORM models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models for metadata registration side effects.
import fahimni.models  # noqa: E402,F401