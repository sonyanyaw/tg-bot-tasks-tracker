from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def need_reminder_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔔 Да", callback_data="reminder:yes"),
                InlineKeyboardButton(text="🚫 Нет", callback_data="reminder:no")
            ]
        ]
    )


def reminder_before_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏰ За 5 мин", callback_data="before:5"),
                InlineKeyboardButton(text="⏰ За 15 мин", callback_data="before:15"),
            ],
            [
                InlineKeyboardButton(text="⏰ За 1 час", callback_data="before:60"),
                InlineKeyboardButton(text="⏰ За день", callback_data="before:1440"),
            ],
            [InlineKeyboardButton(text="➡️ Далее", callback_data="before:next")]
        ]
    )


def reminder_after_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔁 Каждые 30 мин", callback_data="after:30"),
                InlineKeyboardButton(text="🔁 Каждый час", callback_data="after:60"),
            ],
            [
                InlineKeyboardButton(text="🔁 Раз в день", callback_data="after:1440"),
            ],
            [InlineKeyboardButton(text="➡️ Далее", callback_data="after:next")]
        ]
    )


