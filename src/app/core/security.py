from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from src.app.settings import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class Security:
    @classmethod
    def hash_password(cls, password: str) -> str:
        return pwd_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def create_access_token(cls, subject: str, extra: dict[str, Any] | None = None):
        payload: dict[str, Any] = {"sub": subject}
        if extra:
            payload.update(extra)
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_EXPIRE_MINUTES
        )
        payload["exp"] = expire
        return jwt.encode(
            claims=payload, key=settings.JWT_SECRET, algorithm=settings.JWT_ALG
        )

    @classmethod
    def create_refresh_token(cls, subject: str) -> str:
        payload: dict[str, Any] = {"sub": subject}
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_EXPIRE_DAYS
        )
        payload["exp"] = expire
        payload["type"] = "refresh"
        return jwt.encode(
            claims=payload, key=settings.JWT_SECRET, algorithm=settings.JWT_ALG
        )

    @classmethod
    def decode_token(cls, token: str) -> dict[str, Any]:
        return jwt.decode(
            token=token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALG]
        )
