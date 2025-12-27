from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def units_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Минуты", callback_data="unit:minutes"),
            InlineKeyboardButton(text="Секунды", callback_data="unit:seconds"),
        ]
    ])
