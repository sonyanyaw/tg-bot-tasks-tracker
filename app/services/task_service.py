from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.db.models.task_schedule import TaskSchedule
from app.db.session import get_session
from app.db.models.task import Task
from app.db.models.reminder import Reminder
from app.db.models.user import User
from app.services.reminder_service import ReminderService
from app.utils.enums import TaskRepeatRule
from app.db.models.task_status import TaskStatus
from app.utils.enums import TaskStatusEnum

class TaskService:

    @staticmethod
    async def create_task_from_fsm(telegram_user, data: dict):
        """
        Создаём задачу из данных FSM (бота), включая напоминания и расписание.
        Ожидаем:
            data["title"]: str
            data["time"]: datetime.time (для одноразовых задач)
            data["weekdays"]: list[int] (0=Пн ... 6=Вс)
            data["times"]: list[datetime.time] (время для каждого дня)
            data["repeat"]: str
            data["need_reminder"]: bool
            data["reminder_start_before"]: int
            data["reminder_before"]: int
            data["reminder_after"]: int
            data["reminder_after_end"]: datetime.time
        """
        async with get_session() as session:
            user = await session.scalar(
                select(User).where(User.telegram_id == telegram_user.id)
            )
            if not user:
                raise RuntimeError("User not found in DB")

            # создаём задачу с ориентиром due_at
            task = Task(
                title=data["title"],
                user_id=user.id,
                due_at=TaskService._build_due_at(user, data),
                repeat_rule=TaskRepeatRule(data.get("repeat", "none")),
                is_active=True,
            )
            session.add(task)
            await session.flush()  # чтобы получить task.id
            print(f"[DEBUG] Task added: id={task.id}, title={task.title}")

            # создаём напоминание
            if data.get("need_reminder"):
                await ReminderService.create_reminder(
                    session=session,
                    task=task,
                    data={
                        "reminder_start_before": data.get("reminder_start_before", 10),
                        "reminder_before": data.get("reminder_before", 10),
                        "reminder_after": data.get("reminder_after", 5),
                        "reminder_after_end": data.get("reminder_after_end", None),
                        "reminder_before_unit": data.get("reminder_before_unit", "minutes"),  # new
                        "reminder_after_unit": data.get("reminder_after_unit", "minutes")
                    }
                )
                print(f"[DEBUG] Reminder scheduled for task_id={task.id}")

            # создаём расписание (TaskSchedule) только если есть weekdays и times
            weekdays = data.get("weekdays") or []
            times = data.get("times") or []

            if weekdays and times:
                # каждому дню соответствует своё время
                for weekday, time_obj in zip(weekdays, times):
                    schedule = TaskSchedule(
                        task_id=task.id,
                        weekday=weekday,
                        task_time=time_obj
                    )
                    session.add(schedule)
                    await session.flush()
                    print(f"[DEBUG] TaskSchedule added: task_id={task.id}, weekday={weekday}, task_time={time_obj}")

            await session.commit()
            print(f"[DEBUG] Session committed for task_id={task.id}")

            return task

    @staticmethod
    def _build_due_at(user, data: dict) -> datetime:
        """
        Возвращает ближайший due_at для задачи как ориентир.
        Для одноразовой задачи (без расписания) берём data["time"].
        Для повторяющихся задач с расписанием берём первый ближайший день и время.
        """
        user_tz = ZoneInfo(user.timezone)
        today = datetime.now(user_tz).date()
        print('[DEBUG] TODAY TIME', today, datetime.now())

        weekdays = data.get("weekdays") or []
        times = data.get("times") or []

        if weekdays and times:
            # первый день и время
            first_weekday = weekdays[0]
            first_time = times[0]

            delta_days = (first_weekday - today.weekday()) % 7
            first_date = today + timedelta(days=delta_days)

            local_dt = datetime.combine(first_date, first_time, tzinfo=user_tz)
        else:
            # fallback на одноразовую задачу
            local_dt = datetime.combine(today, data["time"], tzinfo=user_tz)

        return local_dt.astimezone(ZoneInfo("UTC"))

    @staticmethod
    async def mark_done(task_id: int, task_date):
        async with get_session() as session:
            status = await session.scalar(
                select(TaskStatus)
                .where(TaskStatus.task_id == task_id)
                .where(TaskStatus.task_date == task_date)
            )

            if status:
                status.status = TaskStatusEnum.done
            else:
                status = TaskStatus(
                    task_id=task_id,
                    task_date=task_date,
                    status=TaskStatusEnum.done
                )
                session.add(status)

            await session.commit()

    @staticmethod
    async def get_completed_today(user_id: int):
        today = datetime.now(timezone.utc).date()
        print('[DEBUG] today', today, user_id)

        async with get_session() as session:
            result = await session.execute(
                select(Task)
                .join(TaskStatus, TaskStatus.task_id == Task.id)
                .where(Task.user_id == user_id)
                .where(TaskStatus.task_date == today)
                .where(TaskStatus.status == TaskStatusEnum.done)
            )
            print('[DEBUG] result', result)
            return result.scalars().all()

        
    


    @staticmethod
    async def get_today_tasks(user_id: int):
        async with get_session() as session:
            user = await session.scalar(
                select(User).where(User.id == user_id)
            )

            user_tz = ZoneInfo(user.timezone)
            today = datetime.now(user_tz).date()

            result = await session.execute(
                select(Task, TaskStatus)
                .options(selectinload(Task.schedules))
                .outerjoin(
                    TaskStatus,
                    and_(
                        TaskStatus.task_id == Task.id,
                        TaskStatus.task_date == today
                    )
                )
                .where(Task.user_id == user_id)
                .where(Task.is_active == True)
            )

            tasks = []

            for task, status in result.all():
                include_today = False

                if task.repeat_rule == TaskRepeatRule.none:
                    local_due_date = task.due_at.astimezone(user_tz).date()
                    include_today = local_due_date == today
                else:
                    for sched in task.schedules:
                        if sched.weekday == today.weekday():
                            include_today = True
                            break

                if include_today:
                    task.today_status = status.status if status else TaskStatusEnum.pending
                    tasks.append(task)

            return tasks
