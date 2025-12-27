from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def snooze_keyboard(task_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ 5 мин",
                    callback_data=f"task_snooze:{task_id}:5"
                ),
                InlineKeyboardButton(
                    text="➕ 15 мин", 
                    callback_data=f"task_snooze:{task_id}:15"
                ),
                InlineKeyboardButton(
                    text="➕ 30 мин", 
                    callback_data=f"task_snooze:{task_id}:30"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", 
                    callback_data=f"task_snooze_back:{task_id}"
                )
            ]
        ]
    )
