"""JWT token creation/verification and password hashing utilities."""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from jose import JWTError, jwt  # type: ignore[import-untyped]
from passlib.context import CryptContext

from fahimni.core.config import settings

logger = logging.getLogger(__name__)

# Use pbkdf2_sha256 so long passwords are supported without bcrypt backend issues.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": expire}
    return cast(str, jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm))


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return cast(dict[str, Any], decoded)
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc