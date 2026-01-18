from typing import AsyncGenerator, Callable
import uuid
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis
from app.models.user import User
from app.core.database import db_helper
from app.core.config import settings

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with db_helper.session_factory() as session:
        yield session

async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf-8",
        decode_responses=True
    )
    try:
        yield redis
    finally:
        await redis.close()

async def get_current_user(
        request: Request,
        db: AsyncSession = Depends(get_db),
        redis: aioredis.Redis = Depends(get_redis)
) -> User:
    cookie_name = getattr(settings, "SESSION_COOKIE_KEY", "session_id")
    session_id = request.cookies.get(cookie_name)

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user_id_str = await redis.get(f"session:{session_id}")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session data"
        )

    user = await db.get(User, user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

def get_current_user_with_verification(need_email_confirm: bool = True) -> Callable:

    async def _check_user(user: User = Depends(get_current_user)) -> User:
        if need_email_confirm:
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Email not verified. Please confirm your email address."
                )
        return user

    return _check_user
