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

back_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Изменить предыдущее поле"),
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
