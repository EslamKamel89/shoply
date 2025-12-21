from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.apps.auth.models import RefreshToken, User
from app.core.security import Security


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, token: str) -> RefreshToken:
        record = RefreshToken(user_id=user_id, token=token)
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        await self.session.commit()
        return record

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def revoke(self, token_id: int) -> None:
        stmt = (
            update(RefreshToken).where(RefreshToken.id == token_id).values(revoked=True)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def revoke_all_token_for_user(self, user_id: int) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(revoked=True)
        )
        await self.session.execute(stmt)
        await self.session.commit()


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, email: str, password: str, role: str = "user") -> User:
        user = User(email=email, password=Security.hash_password(password), role=role)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        await self.session.commit()
        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.lower().strip())
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
