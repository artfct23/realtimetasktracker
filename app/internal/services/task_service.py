from uuid import UUID
from typing import List
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.internal.repository.task import TaskRepository
from app.internal.repository.project import ProjectRepository
from app.schemas.task import TaskCreate, TaskResponse


from app.tasks.background import notify_task_created

class TaskService:
    def __init__(self, db: AsyncSession):
        self.repo = TaskRepository(db)
        self.project_repo = ProjectRepository(db)

    async def create_task(self, project_id: UUID, schema: TaskCreate) -> TaskResponse:
        project = await self.project_repo.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        task_data = schema.model_dump()
        task_data["project_id"] = project_id

        new_task_dto = await self.repo.create(task_data)

        await notify_task_created.kiq(str(new_task_dto.id), str(project_id), new_task_dto.title)

        return new_task_dto

    async def get_tasks_by_project(self, project_id: UUID) -> List[TaskResponse]:
        project = await self.project_repo.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        return await self.repo.get_by_project(project_id)

