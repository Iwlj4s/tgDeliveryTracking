# Aiogram Imports #
from aiogram import F, Router

from aiogram.filters import CommandStart, Command, StateFilter, or_f

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.types import Message

# My Imports #
from keyboards.reply import main_keyboard

user_private_router = Router()


# Start
@user_private_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Hi, {message.from_user.first_name} !",
                         reply_markup=main_keyboard)


# Cancel handler
@user_private_router.message(StateFilter("*"), F.text.lower() == "отмена")  # "отмена" == "cancel"
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    print("State Clear")
    await message.answer("State Clear",
                         reply_markup=main_keyboard)


# Echo answer func
@user_private_router.message()
async def echo_answer(message: Message):
    await message.answer(f"You say: {message.text}")
