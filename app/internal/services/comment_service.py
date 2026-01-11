from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.internal.repository.base import BaseRepository
from app.models.domain import Comment, Task
from app.schemas.comment import CommentCreate
from app.services.realtime import broadcast_message


class CommentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BaseRepository(Comment, db)

    async def add_comment(self, task_id: UUID, schema: CommentCreate, author_id: UUID):
        task = await self.db.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        comment = Comment(
            text=schema.text,
            task_id=task_id,
            author_id=author_id
        )
        self.db.add(comment)
        await self.db.commit()

        await broadcast_message(
            f"project:{task.project_id}",
            "comment.created",
            {"task_id": str(task_id), "text": comment.text}
        )

        return comment
