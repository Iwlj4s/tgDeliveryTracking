from aiogram.fsm.state import StatesGroup, State


class GetTrack(StatesGroup):
    track_data = {}
    user_add_track = False
    track_for_change = None

    user_description = State()

    user_track = State()

    track_after_add_track = State()

    texts = {
        'GetTrack:user_description': 'Измените описание',
    }
