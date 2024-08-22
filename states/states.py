from aiogram.fsm.state import StatesGroup, State


class GetTrack(StatesGroup):
    user_add_track = False

    user_description = State()
    user_delivery_service = State()
    user_delivery_region = State()

    user_track = State()

    track_after_add_track = State()
