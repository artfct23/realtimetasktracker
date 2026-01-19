from uuid import UUID
from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.internal.repository.comment import CommentRepository
from app.internal.repository.task import TaskRepository
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.realtime import broadcast_message

class CommentService:
    def __init__(self, db: AsyncSession):
        self.repo = CommentRepository(db)
        self.task_repo = TaskRepository(db)

    async def create_comment(self, task_id: UUID, comment_in: CommentCreate, author_id: UUID) -> CommentResponse:
        task = await self.task_repo.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        new_comment_dto = await self.repo.create(comment_in, task_id, author_id)

        await broadcast_message(
            f"project:{task.project_id}",
            "comment.created",
            {"task_id": str(task_id), "text": new_comment_dto.text}
        )
        return new_comment_dto

    async def get_comments_by_task(self, task_id: UUID) -> List[CommentResponse]:
        return await self.repo.get_by_task(task_id)

