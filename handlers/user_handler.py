# Aiogram Imports #
from aiogram import F, Router

from aiogram.filters import CommandStart, Command, StateFilter, or_f

from aiogram.fsm.context import FSMContext

from aiogram.types import Message, ReplyKeyboardRemove

# My Imports #
from data.get_track_data import get_track_data_for_user

from keyboards.reply import main_keyboard, choose_track_website_keyboard, choose_delivery_region_keyboard, \
    cancel_keyboard

from states.states import GetTrack

user_private_router = Router()
get_track_states = GetTrack()  # Import StatesGroup


# Start
@user_private_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Данный бот позволяет отслеживать посылки",
                         reply_markup=main_keyboard)


# Cancel handler
@user_private_router.message(StateFilter("*"), F.text.lower() == "отмена")  # "отмена" == "cancel"
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    print("State Clear")
    await message.answer("Все действия отменены",
                         reply_markup=main_keyboard)


# User press track mail
@user_private_router.message(F.text.lower() == "отследить посылку")
@user_private_router.message(StateFilter(None))
async def track(message: Message, state: FSMContext):
    await message.answer("Выберите где вы хотите отследить посылку",
                         reply_markup=choose_track_website_keyboard)

    # Go to get user's delivery service state #
    await state.set_state(get_track_states.user_delivery_service)


# Get user's delivery service
@user_private_router.message(get_track_states.user_delivery_service, F.text)
async def get_user_delivery_service(message: Message, state: FSMContext):
    await state.update_data(user_delivery_service=message.text.lower())
    print(message.text.lower())

    # If user choose "почта россии" -> he need choose delivery region for get standard for track #
    if message.text.lower() == "почта россии":
        print("User's region == Почта России")
        await message.answer("Выберите регион доставки\n"
                             "Это нужно, чтобы проверить Ваш трек, у почты россии есть стандарты трек номеров\n\n"
                             "Трек-номер отправлений по России состоит из 14 цифр. Его вводят без пробелов и скобок — "
                             "например, 45005145009749.\n"
                             "Трек-номер международных отправлений состоит из 13 символов, в нём используются "
                             "латинские заглавные буквы и цифры. Его также вводят без пробелов и скобок — например, "
                             "CA123466789RU.",
                             reply_markup=choose_delivery_region_keyboard)

        # Go to get user's delivery region state #
        await state.set_state(get_track_states.user_delivery_region)
    else:
        print("User's region == Что то другое ")
        await state.update_data(user_region=str(""))

        await message.answer("Введите трек номер: ")
        # Go to get user's track state #
        await state.set_state(get_track_states.user_track)


# Get user's delivery region #
@user_private_router.message(get_track_states.user_delivery_region, F.text)
async def get_user_delivery_region(message: Message, state: FSMContext):
    await state.update_data(user_delivery_region=message.text.lower())
    print(message.text.lower())

    await message.answer("Введите трек номер: ",
                         reply_markup=cancel_keyboard)
    # Go to get user's track state #
    await state.set_state(get_track_states.user_track)


# Get user's track
@user_private_router.message(get_track_states.user_track, F.text)
async def get_user_track(message: Message, state: FSMContext):
    await state.update_data(user_track=message.text.lower())
    print(f"User track: {message.text.lower()}")

    data = await state.get_data()
    user_delivery_service = data.get("user_delivery_service")
    user_region = data.get("user_delivery_region")
    user_track = data.get("user_track")

    print(f"Delivery service: {user_delivery_service}")
    print(f"User region: {user_region}")
    print(f"User track: {user_track}")

    data = get_track_data_for_user(
        user_url=user_delivery_service,
        user_track_region=user_region,
        user_tracking_numbers=user_track)
    print("printing data in user handler",data)

    if data.get("error"):
        error = data.get("error")
        print(error)
        await message.answer(error,
                             reply_markup=cancel_keyboard)

        return

    else:
        print("Track title: (in user_handler)", data.get("track_title"))

        await message.answer(f"{data.get("track_title")}\n"
                             f"{data.get("track_numbers")}\n"
                             f"{data.get("track_location")}\n"
                             f"{data.get("track_status")}\n"
                             f"{data.get("track_info_title")}\n"
                             f"{data.get("track_info_description")}",
                             reply_markup=main_keyboard)

    await state.clear()
