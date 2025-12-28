from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.db.models.reminder_message import ReminderMessage
from app.db.models.task_status import TaskStatus
from app.services.reminder_service import ReminderService
from app.db.session import get_session
from app.db.models.task import Task
from app.services.scheduler_utils import cancel_task_jobs
from app.services.reminder_utils import calculate_next_due
from app.services.task_status_service import TaskStatusService
from app.services.task_service import TaskService
from app.utils.enums import TaskRepeatRule, TaskStatusEnum
from aiogram.exceptions import TelegramBadRequest


router = Router()


@router.callback_query(lambda c: c.data.startswith("task_done"))
async def task_done_handler(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])
    current_message_id = callback.message.message_id

    async with get_session() as session:
        result = await session.execute(
            select(Task)
            .options(
                selectinload(Task.user),
                selectinload(Task.schedules),
                selectinload(Task.reminder),
            )
            .where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            return

        user_tz = ZoneInfo(task.user.timezone)
        # due_local = task.due_at.astimezone(user_tz)

        # Убираем текущие напоминания
        cancel_task_jobs(task_id)

        # Удаляем сообщения-напоминания (кроме текущего)
        result = await session.execute(
            select(ReminderMessage).where(ReminderMessage.task_id == task_id)
        )
        for msg in result.scalars():
            if msg.message_id != current_message_id:
                try:
                    await callback.bot.delete_message(msg.chat_id, msg.message_id)
                except Exception:
                    pass
                await session.delete(msg)


        today = datetime.now(user_tz).date()
        status = await session.scalar(
            select(TaskStatus).where(
                TaskStatus.task_id == task_id,
                TaskStatus.task_date == today
            )
        )

        if not status:
            session.add(TaskStatus(
                task_id=task_id,
                task_date=today,
                status=TaskStatusEnum.done
            ))
        else:
            status.status = TaskStatusEnum.done

        # Определяем тип задачи
        is_repeating = task.repeat_rule in (
            TaskRepeatRule.daily,
            TaskRepeatRule.weekly,
        )


        if not is_repeating:
            # 🧨 Одноразовая задача
            task.is_active = False
            task.is_completed = True
            task.completed_at = datetime.utcnow()

        else:
            # Повторяющаяся задача
            if is_repeating and task.repeat_rule == TaskRepeatRule.daily:
                next_due = task.due_at.astimezone(user_tz) + timedelta(days=1)
            else:
                next_due = calculate_next_due(task, user_tz, True)

            if next_due:
                # Обновляем due_at на будущее 
                task.due_at = next_due.astimezone(ZoneInfo("UTC"))
                task.completed_at = datetime.utcnow()
                
                await session.commit()

                if task.reminder:
                    ReminderService.schedule_reminders(
                        task=task,
                        reminder=task.reminder,
                        due=next_due,
                        user_tz=user_tz
                    )
            else:
                await session.commit()

    try:
        await callback.message.edit_text(callback.message.text + "\n\n✅ Задача выполнена")
    except TelegramBadRequest:
        pass # Если сообщение не изменилось
    await callback.answer("Отлично! 🎉")