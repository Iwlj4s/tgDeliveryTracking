from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="MainKey1"),
            KeyboardButton(text="MainKey2"),
            KeyboardButton(text="MainKey3"),
            KeyboardButton(text="Отмена"),  # Cancel Button
        ]
    ]
)
