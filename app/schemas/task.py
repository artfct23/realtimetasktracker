from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.task import TaskStatus, TaskPriority

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    deadline: Optional[datetime] = None
    assignee_id: Optional[UUID] = None


class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

