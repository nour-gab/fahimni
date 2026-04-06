"""Shared schema mixins for Pydantic v2 response models."""

from pydantic import BaseModel, ConfigDict


class ORMBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
