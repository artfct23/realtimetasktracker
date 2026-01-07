from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.domain import User
from app.schemas.user import UserResponse
from app.services.s3 import upload_file_to_s3
from app.services.realtime import broadcast_message

router = APIRouter()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/me/avatar")
async def upload_avatar(
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    file_url = await upload_file_to_s3(file, f"avatars/{current_user.id}/{file.filename}")
    if not file_url:
        raise HTTPException(status_code=500, detail="Failed to upload file")

    current_user.avatar_url = file_url
    await db.commit()
    await db.refresh(current_user)

    await broadcast_message(f"user:{current_user.id}", "avatar.updated", {"url": file_url})

    return {"avatar_url": file_url}
