from uuid import UUID
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.s3 import upload_file_to_s3
from app.services.realtime import broadcast_message


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_profile(self, user_id: UUID) -> User:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def upload_avatar(self, current_user: User, filename: str, file) -> str:
        file_url = await upload_file_to_s3(file, filename)
        if not file_url:
            raise HTTPException(status_code=500, detail="Failed to upload file")

        current_user.avatar_url = file_url
        await self.db.commit()
        await self.db.refresh(current_user)

        await broadcast_message(
            f"user:{current_user.id}",
            "avatar.updated",
            {"url": file_url}
        )

        return file_url
