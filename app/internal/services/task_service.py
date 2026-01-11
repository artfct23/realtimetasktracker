from uuid import UUID
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.internal.repository.task import TaskRepository
from app.internal.repository.project import ProjectRepository
from app.schemas.task import TaskCreate
from app.models.domain import Attachment
from app.tasks.background import notify_task_created
from app.services.s3 import upload_file_to_s3 


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db  # Нужен для сохранения вложений (Attachment)
        self.repo = TaskRepository(db)
        self.project_repo = ProjectRepository(db)

    async def create_task(self, project_id: UUID, schema: TaskCreate):
        # 1. Проверяем проект
        project = await self.project_repo.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # 2. Создаем задачу
        task_data = schema.model_dump()
        task_data["project_id"] = project_id
        new_task = await self.repo.create(task_data)

        # 3. Запускаем фоновую задачу (уведомление)
        await notify_task_created.kiq(str(new_task.id), str(project_id), new_task.title)

        return new_task

    async def upload_file(self, task_id: UUID, file: UploadFile):
        # 1. Проверяем задачу
        task = await self.repo.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # 2. Загружаем в S3
        url = await upload_file_to_s3(file, f"tasks/{task_id}/{file.filename}")
        if not url:
            raise HTTPException(status_code=500, detail="Upload failed")

        # 3. Сохраняем инфо о файле в БД
        # (Тут можно было бы сделать AttachmentRepository, но для краткости так)
        attachment = Attachment(
            file_name=file.filename,
            file_url=url,
            task_id=task_id,
            file_size=file.size
        )
        self.db.add(attachment)
        await self.db.commit()
        return url
