from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.internal.services.user_service import UserService

router = APIRouter()


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: UUID,
    service: UserService = Depends(get_user_service)
):
    return await service.get_user_profile(user_id)


@router.post("/me/avatar")
async def upload_avatar(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        service: UserService = Depends(get_user_service)
):
    file_url = await service.upload_avatar(
        current_user=current_user,
        filename=f"avatars/{current_user.id}/{file.filename}",
        file=file
    )
    return {"avatar_url": file_url}

