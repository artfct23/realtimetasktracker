from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.internal.repository.base import BaseRepository
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse


class TaskRepository(BaseRepository[Task, TaskCreate, TaskCreate]):
    def __init__(self, session):
        super().__init__(Task, session)

    async def create(self, obj_in: dict) -> TaskResponse:
        if isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            obj_data = obj_in.model_dump()

        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return TaskResponse.model_validate(db_obj)

    async def get_by_project(self, project_id: UUID) -> List[TaskResponse]:
        query = select(Task).where(Task.project_id == project_id)
        result = await self.session.execute(query)
        tasks_orm = result.scalars().all()
        return [TaskResponse.model_validate(t) for t in tasks_orm]
