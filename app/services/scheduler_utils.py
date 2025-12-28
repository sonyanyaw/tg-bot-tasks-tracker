from datetime import datetime
from app.core.scheduler import scheduler


def cancel_task_jobs(task_id: int):
    # due_key = due.strftime("%Y%m%d%H%M")

    for job in scheduler.get_jobs():
        if job.id.startswith(f"task_{task_id}_"):
            scheduler.remove_job(job.id)

