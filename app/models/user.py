import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.task import Task
    from app.models.comment import Comment

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    projects_owned: Mapped[List["Project"]] = relationship("Project", back_populates="owner")
    projects_member: Mapped[List["Project"]] = relationship(
        "Project",
        secondary="project_members",
        back_populates="members"
    )
    tasks_assigned: Mapped[List["Task"]] = relationship("Task", back_populates="assignee")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="author")
