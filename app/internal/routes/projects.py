from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse
from app.internal.services.project_service import ProjectService

router = APIRouter()

def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db)

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    return await service.create_project(project_in, current_user.id)

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    return await service.get_user_projects(current_user.id)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    await service.delete_project(project_id, current_user.id)

