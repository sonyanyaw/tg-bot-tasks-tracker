from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def calculate_next_due(task, user_tz: ZoneInfo):
    """Определяем ближайшее выполнение задачи с учетом расписания"""
    if not task.schedules:
        # fallback на due_at, если расписания нет
        return task.due_at.astimezone(user_tz)

    today = datetime.now(user_tz).date()
    now_time = datetime.now(user_tz).time()

    upcoming = sorted(task.schedules, key=lambda s: (s.weekday, s.task_time))
    for sched in upcoming:
        delta_days = (sched.weekday - today.weekday()) % 7
        due_date = today + timedelta(days=delta_days)
        due_dt = datetime.combine(due_date, sched.task_time, tzinfo=user_tz)
        if due_dt > datetime.now(user_tz):
            return due_dt

    # если ничего не найдено — берём первый в следующей неделе
    first_sched = upcoming[0]
    due_date = today + timedelta(days=(first_sched.weekday - today.weekday() + 7) % 7)
    return datetime.combine(due_date, first_sched.task_time, tzinfo=user_tz)

