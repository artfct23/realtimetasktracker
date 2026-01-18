import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.broker import broker_taskiq
from app.core.database import db_helper
from app.services.realtime import broadcast_message
from app.services.ses import send_email
from app.models.project import Project
from app.models.notification import Notification


@broker_taskiq.task
async def send_welcome_email(email: str):
    await send_email(email, "Welcome", "Добро пожаловать в Task Tracker!")


@broker_taskiq.task
async def notify_task_created(task_id: str, project_id: str, title: str):
    async with db_helper.session_factory() as session:
        query = select(Project).options(
            selectinload(Project.members),
            selectinload(Project.owner)
        ).where(Project.id == uuid.UUID(project_id))

        result = await session.execute(query)
        project = result.scalar_one_or_none()

        if project:
            recipients = set(project.members)
            if project.owner:
                recipients.add(project.owner)

            notifications_to_save = []
            for user in recipients:
                note = Notification(
                    user_id=user.id,
                    title="Новая задача",
                    message=f"В проекте '{project.title}' создана задача: {title}",
                    is_read=False
                )
                notifications_to_save.append(note)

            if notifications_to_save:
                session.add_all(notifications_to_save)
                await session.commit()

    await broadcast_message(
        f"project:{project_id}",
        "task.created",
        {"task_id": task_id, "title": title}
    )


@broker_taskiq.task
async def reminder_deadline(task_id: str, email: str, title: str):
    await send_email(email, "Дедлайн близко!", f"Задача '{title}' скоро истекает.")


@broker_taskiq.task
async def export_tasks_to_excel(user_email: str, project_id: str):
    print(f"Exporting tasks for project {project_id} to {user_email}...")
