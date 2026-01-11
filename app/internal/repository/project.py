from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.internal.repository.base import BaseRepository
from app.models.domain import Project

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db):
        super().__init__(Project, db)

    async def get_by_owner(self, owner_id: UUID) -> List[Project]:
        query = select(Project).where(Project.owner_id == owner_id).options(selectinload(Project.owner))
        result = await self.db.execute(query)
        return result.scalars().all()
