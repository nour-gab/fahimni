"""Authentication request/response schemas."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fahimni.models.user import UserRole

from .common import ORMBaseSchema


class RegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    role: UserRole


class LoginRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(ORMBaseSchema):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
