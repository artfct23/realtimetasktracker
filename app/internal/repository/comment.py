from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.internal.repository.base import BaseRepository
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentResponse


class CommentRepository(BaseRepository[Comment, CommentCreate, CommentCreate]):
    def __init__(self, session):
        super().__init__(Comment, session)

    async def create(self, obj_in: CommentCreate, task_id: UUID, author_id: UUID) -> CommentResponse:
        obj_data = obj_in.model_dump()
        obj_data["task_id"] = task_id
        obj_data["author_id"] = author_id

        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        await self.session.commit()

        await self.session.refresh(db_obj, attribute_names=["author"])

        return CommentResponse.model_validate(db_obj)

    async def get_by_task(self, task_id: UUID) -> List[CommentResponse]:
        query = select(Comment).where(Comment.task_id == task_id).options(selectinload(Comment.author))
        result = await self.session.execute(query)
        comments_orm = result.scalars().all()
        return [CommentResponse.model_validate(c) for c in comments_orm]

