from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.db.models.reminder_message import ReminderMessage
from app.db.session import get_session
from app.db.models.task import Task
from app.services.scheduler_utils import cancel_task_jobs
from app.services.task_status_service import TaskStatusService
from app.services.task_service import TaskService
from app.utils.enums import TaskRepeatRule
from aiogram.exceptions import TelegramBadRequest


router = Router()


@router.callback_query(lambda c: c.data.startswith("task_done"))
async def task_done_handler(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])
    current_message_id = callback.message.message_id
    chat_id = callback.message.chat.id

    async with get_session() as session:
        task = await session.get(Task, task_id)
        if not task:
            return

        current_due = task.due_at  # ← важно

        # ❌ отменяем ВСЕ scheduler jobs
        cancel_task_jobs(task_id, current_due)

        # 🔎 получаем все сообщения-напоминания
        result = await session.execute(
            select(ReminderMessage)
            .where(ReminderMessage.task_id == task_id)
        )
        messages = result.scalars().all()

        # 🗑 удаляем все КРОМЕ текущего
        for msg in messages:
            if msg.message_id != current_message_id:
                try:
                    await callback.bot.delete_message(
                        chat_id=msg.chat_id,
                        message_id=msg.message_id
                    )
                except Exception:
                    pass  # сообщение уже удалено / недоступно

                await session.delete(msg)

        await session.commit()

    # await callback.answer("✅ Задача выполнена")


    await callback.message.edit_text(
        callback.message.text + "\n\n✅ Задача выполнена"
    )
    await callback.answer("Отлично! 🎉")