from datetime import timedelta, date
from zoneinfo import ZoneInfo

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.db.models.task import Task
from app.services.reminder_service import ReminderService
from app.services.scheduler_utils import cancel_task_jobs
from app.bot.keyboards.snooze import snooze_keyboard
from app.bot.keyboards.reminder_actions import reminder_actions_keyboard
from app.db.models.task_status import TaskStatus
from app.utils.enums import TaskStatusEnum

router = Router()


@router.callback_query(F.data.startswith("task_snooze_menu:"))
async def snooze_menu(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])

    await callback.message.edit_reply_markup(
        reply_markup=snooze_keyboard(task_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("snooze:"))
async def snooze_handler(callback: CallbackQuery):
    _, task_id, minutes = callback.data.split(":")
    minutes = int(minutes)

    async with get_session() as session:
        result = await session.execute(
            select(Task)
            .options(selectinload(Task.reminder), selectinload(Task.user))
            .where(Task.id == int(task_id))
        )
        task = result.scalar_one_or_none()
        if not task or not task.reminder:
            await callback.answer("Ошибка: напоминание не найдено", show_alert=True)
            return

        # дальше идёт твоя логика snooze:
        task.due_at += timedelta(minutes=minutes)
        await session.commit()

        cancel_task_jobs(task.id)
        ReminderService.schedule_reminders(
            task,
            task.reminder,
            task.due_at,
            ZoneInfo(task.user.timezone)
        )


    await callback.message.answer(f"⏰ Отложено на {minutes} минут")
    await callback.answer()



@router.callback_query(F.data.startswith("task_snooze_back:"))
async def snooze_back(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])

    await callback.message.edit_reply_markup(
        reply_markup=reminder_actions_keyboard(task_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("task_cancel:"))
async def task_cancel_handler(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])
    today = date.today()

    async with get_session() as session:
        task = await session.scalar(
            select(Task).where(Task.id == task_id)
        )
        if not task:
            await callback.answer("Задача не найдена", show_alert=True)
            return

        # ищем статус на сегодня
        status = await session.scalar(
            select(TaskStatus).where(
                TaskStatus.task_id == task_id,
                TaskStatus.task_date == today
            )
        )

        if status:
            status.status = TaskStatusEnum.canceled
        else:
            session.add(TaskStatus(
                task_id=task_id,
                task_date=today,
                status=TaskStatusEnum.canceled
            ))

        await session.commit()

    # отменяем ТОЛЬКО сегодняшние напоминания
    cancel_task_jobs(task_id)

    await callback.message.edit_text(
        callback.message.text + "\n\n❌ Задание отменено на сегодня"
    )
    await callback.answer("Задание отменено на сегодня")