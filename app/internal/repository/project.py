from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.internal.repository.base import BaseRepository
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectResponse

class ProjectRepository(BaseRepository[Project, ProjectCreate, ProjectCreate]):
    def __init__(self, session):
        super().__init__(Project, session)

    async def create(self, obj_in: dict) -> ProjectResponse:
        if isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            obj_data = obj_in.model_dump()

        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return ProjectResponse.model_validate(db_obj)

    async def get_by_owner(self, owner_id: UUID) -> List[ProjectResponse]:
        query = select(Project).where(Project.owner_id == owner_id)
        result = await self.session.execute(query)
        projects_orm = result.scalars().all()
        return [ProjectResponse.model_validate(p) for p in projects_orm]

    async def get(self, id: UUID) -> Optional[ProjectResponse]:
        orm_obj = await self.session.get(self.model, id)
        if not orm_obj:
            return None
        return ProjectResponse.model_validate(orm_obj)

    async def delete_by_owner(self, project_id: UUID, owner_id: UUID) -> bool:
        stmt = delete(Project).where(
            Project.id == project_id,
            Project.owner_id == owner_id
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0


