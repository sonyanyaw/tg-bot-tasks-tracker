from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def calculate_next_due(task, user_tz: ZoneInfo, is_done: bool):
    """
    is_done = True  → пользователь нажал "выполнено" или "отменить"
    is_done = False → автопереход 
    """

    if not task.schedules:
        return task.due_at.astimezone(user_tz)

    now = datetime.now(user_tz)
    base_dt = (
        now
        if not is_done
        else task.due_at.astimezone(user_tz) + timedelta(seconds=1)
    )

    candidates: list[datetime] = []

    for sched in task.schedules:
        delta_days = (sched.weekday - base_dt.weekday()) % 7
        due_date = base_dt.date() + timedelta(days=delta_days)
        due_dt = datetime.combine(due_date, sched.task_time, tzinfo=user_tz)

        if delta_days == 0 and due_dt <= base_dt:
            due_dt += timedelta(days=7)

        candidates.append(due_dt)

    return min(candidates)
