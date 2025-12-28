from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from aiogram import Bot
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.bot.keyboards.reminder_actions import reminder_actions_keyboard
from app.core.scheduler import scheduler
from app.db.models.reminder import Reminder
from app.db.models.reminder_message import ReminderMessage
from app.db.models.task import Task
from app.db.session import get_session
from app.services.scheduler_utils import cancel_task_jobs
from app.services.reminder_utils import calculate_next_due
from app.utils.datetime import format_time_delta

UTC = ZoneInfo("UTC")


class ReminderService:
    _bot: Bot | None = None

    @classmethod
    def set_bot(cls, bot: Bot):
        cls._bot = bot


    @staticmethod
    async def restore_all_reminders():
        """
        Восстанавливает все напоминания из базы данных и добавляет их в scheduler при старте бота.
        """
        async with get_session() as session:
            result = await session.execute(
                select(Task)
                .options(
                    selectinload(Task.reminder),
                    selectinload(Task.user),
                    selectinload(Task.schedules)
                )
                .where(Task.is_active == True)
            )
            tasks = result.scalars().all()
            for task in tasks:
                reminder = task.reminder
                if not reminder:
                    continue
                user_tz = ZoneInfo(task.user.timezone)
                next_due = calculate_next_due(task, user_tz)
                # Если нет следующего события, пропускаем
                if not next_due:
                    continue
                ReminderService.schedule_reminders(task, reminder, next_due, user_tz)
            print(f"[DEBUG] Restored {len(tasks)} reminders into scheduler.")
    

    @staticmethod
    async def create_reminder(session, task: Task, data: dict):
        """
        Создаёт объект Reminder и ставит задачи в scheduler для каждого ближайшего события из расписания.
        """
        # загружаем расписание и пользователя
        result = await session.execute(
            select(Task)
            .options(selectinload(Task.reminder),
                     selectinload(Task.user),
                     selectinload(Task.schedules))
            .where(Task.id == task.id)
        )
        task = result.scalar_one_or_none()
        if not task:
            return

        user_tz = ZoneInfo(task.user.timezone)
        next_due = calculate_next_due(task, user_tz)

        # вычисляем remind_end
        remind_end = datetime.combine(
            next_due.date(),
            data["reminder_after_end"],
            tzinfo=user_tz
        ).astimezone(UTC) if data.get("reminder_after_end") else None

        print("[DEBUG] DATA:", data)


        # создаём объект Reminder
        reminder = Reminder(
            task_id=task.id,
            remind_before=True,
            remind_after=True,
            remind_start=data.get("reminder_start_before", 10),
            interval_before_deadline=data.get("reminder_before", 10),
            interval_after_deadline=data.get("reminder_after", 5),
            interval_before_unit=data.get("reminder_before_unit", "minutes"),  # new
            interval_after_unit=data.get("reminder_after_unit", "minutes"),    # new
            remind_end=remind_end,
        )

        session.add(reminder)
        await session.flush()
        await session.commit()
        print(f"[DEBUG] Reminder added: task_id={task.id}, remind_start={reminder.remind_start}, "
              f"before_interval={reminder.interval_before_deadline}, after_interval={reminder.interval_after_deadline}")


        # ставим напоминания в scheduler
        ReminderService.schedule_reminders(task, reminder, next_due, user_tz)

    @staticmethod
    def schedule_reminders(task: Task, reminder: Reminder, due: datetime, user_tz: ZoneInfo):
        """
        Добавляем в scheduler задачи напоминаний ДО и ПОСЛЕ ближайшего события.
        """
        now = datetime.now(UTC)

        # --- ДО дедлайна ---
        before_start = due - timedelta(minutes=reminder.remind_start)
        start_date = max(before_start, now)
        def build_interval(value: int, unit: str):
            return {"seconds": value} if unit == "seconds" else {"minutes": value}
        
        before_kwargs = build_interval(
            reminder.interval_before_deadline,
            reminder.interval_before_unit
        )
        print("[DEBUG] before_kwargs", before_kwargs)

        if start_date < due:
            scheduler.add_job(
                ReminderService._send_reminder,
                trigger=IntervalTrigger(
                    **before_kwargs,
                    start_date=start_date,
                    end_date=due,
                ),
                args=[task.id, True],
                id=f"task_{task.id}_before_{due.strftime('%Y%m%d%H%M')}",
                replace_existing=True,
            )

            print(f"[DEBUG] Scheduled 'before' reminders for task_id={task.id}, start={start_date}, end={due}")


        # --- ПОСЛЕ дедлайна ---
        after_kwargs = build_interval(
            reminder.interval_after_deadline,
            reminder.interval_after_unit
        )
        
        after_trigger_kwargs = dict(
            **after_kwargs,
            start_date=due,
        )

        if reminder.remind_end:
            after_trigger_kwargs["end_date"] = reminder.remind_end

        scheduler.add_job(
            ReminderService._send_reminder,
            trigger=IntervalTrigger(**after_trigger_kwargs),
            args=[task.id, False],
            id=f"task_{task.id}_after_{due.strftime('%Y%m%d%H%M')}",
            replace_existing=True,
        )
        print(f"[DEBUG] Scheduled 'after' reminders for task_id={task.id}, start={due}, "
              f"end={reminder.remind_end}")

    @staticmethod
    async def _send_reminder(task_id: int, before: bool):
        """Отправка уведомления пользователю."""
        if ReminderService._bot is None:
            print("Bot is not initialized!")
            return
        bot = ReminderService._bot

        async with get_session() as session:
            result = await session.execute(
                select(Task)
                .options(selectinload(Task.reminder), selectinload(Task.user))
                .where(Task.id == task_id)
            )
            task = result.scalar_one_or_none()
            if not task or not task.reminder:
                return


            user_tz = ZoneInfo(task.user.timezone)
            due_local = task.due_at.astimezone(user_tz)
            
            if not task.is_active:
                cancel_task_jobs(task.id, due_local)
                return
                  
            
            now_utc = datetime.now(UTC)
            delta = task.due_at - now_utc
            time_left = format_time_delta(delta)

            if task.reminder.interval_before_unit == "minutes":
                before_unit = "минут"
            else:
                before_unit = "секунд"

            if task.reminder.interval_after_unit == "minutes":
                after_unit = "минут"
            else:
                after_unit = "секунд"

            text = (
                f"⏰ Напоминание!\n\n"
                f"📝 Задача: {task.title}\n"
                f"⏳ Дедлайн: {due_local.strftime('%H:%M')}\n"
                f"⏱ {time_left}\n\n"
                # f"{'До дедлайна' if before else 'После дедлайна'}\n"
                
                # f"Начало напоминаний: {task.reminder.remind_start} мин. до дедлайна\n"
                # f"Интервал до дедлайна: {task.reminder.interval_before_deadline} {before_unit}\n"
                # f"Интервал после дедлайна: {task.reminder.interval_after_deadline} {after_unit}\n"
                f"Окончание напоминаний: "
                f"{task.reminder.remind_end.astimezone(ZoneInfo(task.user.timezone)).strftime('%H:%M') if task.reminder.remind_end else 'не ограничено'}"
            )


            # await bot.send_message(chat_id=task.user.telegram_id, text=text)

            msg = await bot.send_message(
                chat_id=task.user.telegram_id,
                text=text,
                reply_markup=reminder_actions_keyboard(task.id)
            )

            session.add(
                ReminderMessage(
                    task_id=task.id,
                    chat_id=msg.chat.id,
                    message_id=msg.message_id
                )
            )
            await session.commit()


            # await bot.send_message(
            #     chat_id=task.user.telegram_id,
            #     text=text,
            #     reply_markup=reminder_actions_keyboard(task.id)
            # )
            print(f"[DEBUG] Sent reminder for task_id={task.id}, before={before}")

            # Обновляем время последнего уведомления
            task.reminder.last_notified_at = datetime.utcnow()
            await session.commit()
            print(f"[DEBUG] Updated last_notified_at for task_id={task.id}")
