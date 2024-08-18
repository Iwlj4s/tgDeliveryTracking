from aiogram.fsm.state import StatesGroup, State


class GetTrack(StatesGroup):
    user_delivery_service = State()
    user_delivery_region = State()

    user_track = State()

