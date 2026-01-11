from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from app.core.deps import get_db, get_current_user
from app.models.domain import Task, Project, User
from app.schemas.task import TaskCreate, TaskResponse

router = APIRouter()

@router.post("/{project_id}/tasks/", response_model=TaskResponse)
async def create_task(
    project_id: UUID,
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    new_task = Task(
        **task_in.model_dump(),
        project_id=project_id
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

@router.get("/{project_id}/tasks/", response_model=List[TaskResponse])
async def get_project_tasks(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Task).where(Task.project_id == project_id).options(selectinload(Task.assignee))
    result = await db.execute(query)
    return result.scalars().all()
