from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.internal.repository.base import BaseRepository
from app.models.domain import Task

class TaskRepository(BaseRepository[Task]):
    def __init__(self, db):
        super().__init__(Task, db)

    async def get_by_project(self, project_id: UUID) -> List[Task]:
        query = select(Task).where(Task.project_id == project_id).options(selectinload(Task.assignee))
        result = await self.db.execute(query)
        return result.scalars().all()
