from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.internal.services.comment_service import CommentService

router = APIRouter()

def get_comment_service(db: AsyncSession = Depends(get_db)) -> CommentService:
    return CommentService(db)

@router.post("/{task_id}/comments/", response_model=CommentResponse)
async def create_comment(
        task_id: UUID,
        comment_in: CommentCreate,
        current_user: User = Depends(get_current_user),
        service: CommentService = Depends(get_comment_service)
):
    return await service.create_comment(task_id, comment_in, current_user.id)

@router.get("/{task_id}/comments/", response_model=List[CommentResponse])
async def get_comments(
        task_id: UUID,
        service: CommentService = Depends(get_comment_service)
):
    return await service.get_comments_by_task(task_id)

