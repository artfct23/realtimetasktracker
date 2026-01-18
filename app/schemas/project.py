from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse


class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    owner: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)

class ProjectUpdate(ProjectBase):
    title: Optional[str] = None
    description: Optional[str] = None
