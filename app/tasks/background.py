import taskiq_fastapi
from app.broker import broker_taskiq
from app.services.realtime import broadcast_message
from app.services.ses import send_email

@broker_taskiq.task
async def send_welcome_email(email: str):
    await send_email(email, "Welcome", "Добро пожаловать в Task Tracker!")

@broker_taskiq.task
async def notify_task_created(task_id: str, project_id: str, title: str):
    await broadcast_message(
        f"project:{project_id}",
        "task.created",
        {"task_id": task_id, "title": title}
    )

@broker_taskiq.task
async def reminder_deadline(task_id: str, email: str, title: str):
    # Эта задача будет планироваться на будущее
    await send_email(email, "Дедлайн близко!", f"Задача '{title}' просрочена или скоро истечет.")

@broker_taskiq.task
async def export_tasks_to_excel(user_email: str, project_id: str):
    print(f"--- START EXPORT FOR {user_email} ---")
    print(f"Export for project {project_id} completed (Simulated)")
