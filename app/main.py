import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.bot.bot import bot as global_bot
from app.bot.routers import reminder_actions, reminders
from app.core.config import settings
from app.core.scheduler import setup_scheduler
from app.bot import start
from app.bot.handlers.tasks import list_today
from app.bot.handlers.tasks import completed_today
from app.bot.handlers.tasks import add
from app.db.session import wait_for_db, engine
from app.services.reminder_service import ReminderService


async def main():
    global global_bot
    global_bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        # default=DefaultBotProperties(parse_mode="HTML"),
    )
    ReminderService.set_bot(global_bot)

    dp = Dispatcher()

    print('bot started')

    dp.include_router(start.router)
    dp.include_router(list_today.router)
    dp.include_router(completed_today.router)
    dp.include_router(add.router)
    dp.include_router(reminders.router)
    dp.include_router(reminder_actions.router)

    scheduler = setup_scheduler()
    # scheduler.start()
    print("Scheduler started!")

    await wait_for_db(engine)
    # Восстановление напоминаний из базы
    await ReminderService.restore_all_reminders()

    await dp.start_polling(global_bot)


if __name__ == "__main__":
    asyncio.run(main())
