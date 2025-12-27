from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.main_menu import main_menu
from app.services.task_service import TaskService
from app.services.user_service import UserService

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    await UserService.get_or_create_user(message)

    await message.answer(
        "👋 Привет! Я трекер задач и привычек.\n\n"
        "Я буду НАПОМИНАТЬ, пока ты не сделаешь задачу 😈",
        reply_markup=main_menu(),
    )
