from aiogram.fsm.state import StatesGroup, State


class GetTrack(StatesGroup):
    user_add_track = False
    track_for_change = None

    user_description = State()
    user_delivery_service = State()
    user_delivery_region = State()

    user_track = State()

    track_after_add_track = State()

    texts = {
        'GetTrack:user_description': 'Измените описание',
        'GetTrack:user_delivery_service': 'Измените Службу Доставки',
        'GetTrack:user_delivery_region': 'Измените Регион доставки'
    }
