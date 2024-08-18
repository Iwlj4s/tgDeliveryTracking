from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отследить посылку"),
        ]
    ]
)

choose_track_website_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Почта России"),
        ],

        [
            KeyboardButton(text="Отмена"),  # Cancel Button
        ]
    ]
)

choose_delivery_region_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Россия"),
            KeyboardButton(text="Международный"),
        ],

        [
            KeyboardButton(text="Отмена"),  # Cancel Button
        ]
    ]
)
