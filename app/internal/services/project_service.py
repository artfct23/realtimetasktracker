from uuid import UUID
from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.internal.repository.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectResponse

class ProjectService:
    def __init__(self, db: AsyncSession):
        self.repo = ProjectRepository(db)

    async def create_project(self, schema: ProjectCreate, owner_id: UUID) -> ProjectResponse:
        project_data = schema.model_dump()
        project_data["owner_id"] = owner_id
        return await self.repo.create(project_data)

    async def get_user_projects(self, user_id: UUID) -> List[ProjectResponse]:
        return await self.repo.get_by_owner(user_id)

    async def delete_project(self, project_id: UUID, user_id: UUID) -> None:
        is_deleted = await self.repo.delete_by_owner(project_id=project_id, owner_id=user_id)
        if not is_deleted:
            raise HTTPException(status_code=404, detail="Project not found")


