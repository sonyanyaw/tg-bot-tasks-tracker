from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def reminder_action_keyboard(task_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏳ Отложить на 10 мин",
                    callback_data=f"snooze:{task_id}:10",
                ),
                InlineKeyboardButton(
                    text="⏳ На 30 мин",
                    callback_data=f"snooze:{task_id}:30",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✅ Выполнено",
                    callback_data=f"done:{task_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Отменить задачу",
                    callback_data=f"cancel:{task_id}",
                ),
            ],
        ]
    )
