import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, DateTime, Table, func, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task

project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship("User", back_populates="projects_owned")
    members: Mapped[List["User"]] = relationship(
        "User",
        secondary=project_members,
        back_populates="projects_member"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan"
    )
