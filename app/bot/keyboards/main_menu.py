from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Список дел на сегодня")],
            [KeyboardButton(text="📅 Задачи на другие дни")],
            [KeyboardButton(text="✅ Выполненные за сегодня")],
            [KeyboardButton(text="➕ Добавить задачу")],
            [KeyboardButton(text="✏️ Изменить задачу")],
            [KeyboardButton(text="🗑 Удалить задачу")],
        ],
        resize_keyboard=True,
    )
