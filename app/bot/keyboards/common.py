from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def back_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True
    )

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

DAYS = [
    ("Пн", "mon"),
    ("Вт", "tue"),
    ("Ср", "wed"),
    ("Чт", "thu"),
    ("Пт", "fri"),
    ("Сб", "sat"),
    ("Вс", "sun"),
]


def week_days_keyboard(selected: set[str] | None = None):
    selected = selected or set()
    keyboard = []

    for text, value in DAYS:
        prefix = "✅ " if value in selected else ""
        keyboard.append([
            InlineKeyboardButton(
                text=f"{prefix}{text}",
                callback_data=f"day:{value}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="➡️ Готово",
            callback_data="days:done"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def confirm_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data="confirm:yes"
                ),
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="confirm:no"
                ),
            ]
        ]
    )
