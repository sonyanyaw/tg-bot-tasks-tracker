from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def repeat_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Без повторения", callback_data="repeat:none")],
            [InlineKeyboardButton(text="🔁 Каждый день", callback_data="repeat:daily")],
            [InlineKeyboardButton(text="📅 По дням недели", callback_data="repeat:weekly")]
        ]
    )
