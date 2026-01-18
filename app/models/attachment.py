import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.comment import Comment


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_url: Mapped[str] = mapped_column(String, nullable=False)


    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    comment_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"),
                                                            nullable=True)

    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    task: Mapped[Optional["Task"]] = relationship("Task", back_populates="attachments")
    comment: Mapped[Optional["Comment"]] = relationship("Comment", back_populates="attachments")
