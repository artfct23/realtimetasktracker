from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse
from app.internal.services.task_service import TaskService

router = APIRouter()

def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    return TaskService(db)

@router.post("/{project_id}/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: UUID,
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    return await service.create_task(project_id, task_in)

@router.get("/{project_id}/tasks/", response_model=List[TaskResponse])
async def get_project_tasks(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    return await service.get_tasks_by_project(project_id)
