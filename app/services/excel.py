import pandas as pd
from io import BytesIO
from typing import List
from app.models.task import Task


def generate_tasks_excel(tasks: List[Task]) -> bytes:
    data = []
    for task in tasks:
        data.append({
            "ID": str(task.id),
            "Title": task.title,
            "Description": task.description,
            "Status": task.status.value,
            "Priority": task.priority.value,
            "Deadline": task.deadline.replace(tzinfo=None) if task.deadline else None,
            "Created At": task.created_at.replace(tzinfo=None) if task.created_at else None
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tasks')

    return output.getvalue()
