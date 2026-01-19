from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.comment import Comment
from app.models.task import Task
from app.schemas.comment import CommentCreate
from app.services.realtime import broadcast_message

class CommentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_comment(self, task_id: UUID, comment_in: CommentCreate, author_id: UUID) -> Comment:
        task = await self.db.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        new_comment = Comment(
            text=comment_in.text,
            task_id=task_id,
            author_id=author_id
        )
        self.db.add(new_comment)
        await self.db.commit()
        await self.db.refresh(new_comment, attribute_names=["author"])

        await broadcast_message(
            f"project:{task.project_id}",
            "comment.created",
            {"task_id": str(task_id), "text": new_comment.text}
        )
        return new_comment

    async def get_comments_by_task(self, task_id: UUID) -> List[Comment]:
        query = select(Comment).where(Comment.task_id == task_id).options(selectinload(Comment.author))
        result = await self.db.execute(query)
        return result.scalars().all()
