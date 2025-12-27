from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def reminder_actions_keyboard(task_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Выполнено",
                    callback_data=f"task_done:{task_id}"
                ),
                InlineKeyboardButton(
                    text="⏳ Отложить",
                    callback_data=f"task_snooze_menu:{task_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменить задание",
                    callback_data=f"task_cancel:{task_id}"
                )
            ]
        ]
    )
