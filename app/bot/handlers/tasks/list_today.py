from aiogram import Router
from aiogram.types import Message
from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.task_service import TaskService
from app.services.user_service import UserService
from app.db.session import get_session
from app.utils.enums import TaskStatusEnum

router = Router()


@router.message(lambda m: m.text == "📝 Список дел на сегодня")
async def list_today_handler(message: Message):
    async with get_session() as session:
        user = await UserService.get_user_by_telegram_id(
            session=session,
            telegram_id=message.from_user.id
        )

        if not user:
            await message.answer("❌ Вы не зарегистрированы в системе")
            return

    user_tz = ZoneInfo(user.timezone)

    tasks = await TaskService.get_today_tasks(user.id)

    if not tasks:
        await message.answer("📭 На сегодня задач нет")
        return

    status_emojis = {
        TaskStatusEnum.pending: "⏳",
        TaskStatusEnum.done: "✅",
        TaskStatusEnum.canceled: "❌"
    }

    tasks_sorted = sorted(
        tasks,
        key=lambda t: (
            t.due_at.astimezone(user_tz)
            if t.due_at else datetime.max.replace(tzinfo=user_tz)
        )
    )

    today_str = datetime.now(user_tz).strftime("%d.%m.%Y")
    text_lines = [f"📋 *Задачи на сегодня — {today_str}:*"]

    for i, task in enumerate(tasks_sorted, start=1):
        status = status_emojis.get(task.today_status, "⏳")
        time_str = (
            task.due_at.astimezone(user_tz).strftime("%H:%M")
            if task.due_at else "—"
        )
        text_lines.append(f"{i}. {status} {task.title} — {time_str}")

    await message.answer("\n".join(text_lines), parse_mode="Markdown")
