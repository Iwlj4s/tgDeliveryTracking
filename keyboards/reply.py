from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отследить посылку"),
            KeyboardButton(text="Мои треки"),
        ],

        [
            KeyboardButton(text="Добавить трек в 'мои треки'")
        ]
    ]
)

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отмена"),
        ]
    ]
)

skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Пропустить поле"),
            KeyboardButton(text="Отмена")
        ]
    ]
)

cancel_back_skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Пропустить поле"),
        ],

        [
            KeyboardButton(text="Изменить предыдущее поле"),
        ],

        [
            KeyboardButton(text="Отмена")
        ]
    ]
)

choose_track_website_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Почта России"),
        ],

        [
            KeyboardButton(text="Изменить предыдущее поле")
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
            KeyboardButton(text="Изменить предыдущее поле")
        ],

        [
            KeyboardButton(text="Отмена"),  # Cancel Button
        ]
    ]
)

# KEYBOARDS FOR CHANGING TRACK #

change_track_website_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Почта России"),
        ],

        [
            KeyboardButton(text="Пропустить поле"),
        ],

        [
            KeyboardButton(text="Отмена"),  # Cancel Button
        ]
    ]
)

change_delivery_region_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Россия"),
            KeyboardButton(text="Международный"),
        ],

        [
            KeyboardButton(text="Пропустить поле"),
        ],

        [
            KeyboardButton(text="Отмена"),  # Cancel Button
        ]
    ]
)
