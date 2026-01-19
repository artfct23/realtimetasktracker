import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis
from typing import Optional
from app.internal.repository.user import UserRepository
from app.schemas.user import UserCreate, UserLogin
from app.core.security import get_password_hash, verify_password
from app.services.ses import send_email


class AuthService:
    def __init__(self, db: AsyncSession, redis: aioredis.Redis):
        self.repo = UserRepository(db)
        self.redis = redis

    async def register_user(self, user_in: UserCreate):
        if await self.repo.get_by_email(user_in.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        user_data = {
            "email": user_in.email,
            "hashed_password": get_password_hash(user_in.password),
            "full_name": user_in.full_name,
            "is_active": True
        }

        new_user = await self.repo.create(user_data)
        await send_email(new_user.email, "Welcome", "Добро пожаловать в Task Tracker!")
        return new_user

    async def login_user(self, user_in: UserLogin) -> tuple[str, int]:
        user = await self.repo.get_by_email(user_in.email)

        if not user or not verify_password(user_in.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect email or password")

        session_id = str(uuid.uuid4())
        session_ttl = 86400
        await self.redis.setex(f"session:{session_id}", session_ttl, str(user.id))

        return session_id, session_ttl

    async def logout_user(self, session_id: Optional[str]) -> None:
        if session_id:
            await self.redis.delete(f"session:{session_id}")

