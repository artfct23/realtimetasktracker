import uuid
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from redis import asyncio as aioredis

from app.core.deps import get_db, get_redis, get_current_user
from app.models.domain import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.security import get_password_hash, verify_password
from app.services.ses import send_email

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    await send_email(new_user.email, "Welcome", "Welcome to Task Tracker!")

    return new_user


@router.post("/login")
async def login(
        response: Response,
        user_in: UserLogin,
        db: AsyncSession = Depends(get_db),
        redis: aioredis.Redis = Depends(get_redis)
):
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    session_id = str(uuid.uuid4())
    await redis.setex(f"session:{session_id}", 86400, str(user.id))

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=86400,
        samesite="lax",
        secure=False
    )

    return {"message": "Logged in successfully"}


@router.post("/logout")
async def logout(
        request: Request,
        response: Response,
        redis: aioredis.Redis = Depends(get_redis)
):
    session_id = request.cookies.get("session_id")
    if session_id:
        await redis.delete(f"session:{session_id}")

    response.delete_cookie("session_id")
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
