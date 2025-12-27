from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler(timezone=ZoneInfo("UTC"))

def setup_scheduler():
    """Инициализация и запуск планировщика."""
    scheduler.start()
    return scheduler
