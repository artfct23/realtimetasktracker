from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.internal.repository.project import ProjectRepository
from app.schemas.project import ProjectCreate


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.repo = ProjectRepository(db)

    async def create_project(self, schema: ProjectCreate, owner_id: UUID):
        project_data = schema.model_dump()
        project_data["owner_id"] = owner_id
        return await self.repo.create(project_data)

    async def delete_project(self, project_id: UUID, user_id: UUID):
        project = await self.repo.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        if project.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        await self.repo.delete(project_id)
