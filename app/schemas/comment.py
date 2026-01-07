from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: UUID
    task_id: UUID
    author: UserResponse
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
