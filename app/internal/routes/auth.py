from fastapi import APIRouter, Depends, Response, Request, status, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis
from typing import Optional
from app.core.deps import get_db, get_redis, get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.internal.services.auth_service import AuthService

router = APIRouter()

def get_auth_service(
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis)
) -> AuthService:
    return AuthService(db, redis)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    service: AuthService = Depends(get_auth_service)
):
    return await service.register_user(user_in)

@router.post("/login")
async def login(
    response: Response,
    user_in: UserLogin,
    service: AuthService = Depends(get_auth_service)
):
    session_id, session_ttl = await service.login_user(user_in)

    response.set_cookie(
        key=settings.SESSION_COOKIE_KEY,
        value=session_id,
        httponly=True,
        max_age=session_ttl,
        samesite="lax",
        secure=False
    )
    return {"message": "Logged in successfully"}

@router.post("/logout")
async def logout(
    response: Response,
    session_id: Optional[str] = Cookie(alias=settings.SESSION_COOKIE_KEY, default=None),
    service: AuthService = Depends(get_auth_service)
):
    await service.logout_user(session_id)
    response.delete_cookie(settings.SESSION_COOKIE_KEY)
    return {"message": "Logged out"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


