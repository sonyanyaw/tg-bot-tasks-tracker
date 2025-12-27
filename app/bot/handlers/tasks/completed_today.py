from aiogram import Router
from aiogram.types import Message

from app.services.task_service import TaskService
from app.services.user_service import UserService
from app.db.session import get_session

router = Router()


@router.message(lambda m: m.text == "✅ Выполненные за сегодня")
async def completed_tasks_handler(message: Message):
    # tasks = await TaskService.get_completed_today(message.from_user.id)

    # print(tasks)
    async with get_session() as session:
        # Получаем ID пользователя из БД по его Telegram ID
        user_db_id = await UserService.get_user_id_by_telegram_id(
            session=session,
            telegram_id=message.from_user.id
        )

        if not user_db_id:
            await message.answer("❌ Вы не зарегистрированы в системе")
            return
        print('[DEBUG] user_db_id', user_db_id)
        # Теперь используем ID из БД вместо Telegram ID
        tasks = await TaskService.get_completed_today(user_db_id)

    print('[DEBUG] tasks', tasks)
    if not tasks:
        await message.answer("❌ Сегодня нет выполненных задач")
        return

    text = "✅ Выполненные задачи:\n\n"
    for task in tasks:
        text += f"✔ {task.title}\n"

    await message.answer(text)
