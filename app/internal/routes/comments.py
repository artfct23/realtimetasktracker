from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List

from app.core.deps import get_db, get_current_user
from app.models.domain import Comment, Task, User
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.realtime import broadcast_message

router = APIRouter()


@router.post("/{task_id}/comments/", response_model=CommentResponse)
async def create_comment(
        task_id: UUID,
        comment_in: CommentCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    new_comment = Comment(
        text=comment_in.text,
        task_id=task_id,
        author_id=current_user.id
    )
    db.add(new_comment)
    await db.commit()

    await db.refresh(new_comment, attribute_names=["author"])

    await broadcast_message(
        f"project:{task.project_id}",
        "comment.created",
        {"task_id": str(task_id), "text": new_comment.text}
    )

    return new_comment


@router.get("/{task_id}/comments/", response_model=List[CommentResponse])
async def get_comments(
        task_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = select(Comment).where(Comment.task_id == task_id).options(selectinload(Comment.author))
    result = await db.execute(query)
    return result.scalars().all()
