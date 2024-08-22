# Aiogram Imports #
from aiogram import F, Router

from aiogram.filters import CommandStart, StateFilter, or_f

from aiogram.fsm.context import FSMContext

from aiogram.types import Message, CallbackQuery

# sqlalchemy Imports #
from sqlalchemy.ext.asyncio import AsyncSession

# My Imports #
from data.get_track_data import get_track_data_for_user
from database.orm_query import orm_get_user_tracks, orm_delete_user_track, orm_add_user_track
from keyboards.inline import get_callback_btns

from keyboards.reply import main_keyboard, choose_track_website_keyboard, choose_delivery_region_keyboard, \
    cancel_keyboard, skip_keyboard

from data.parsing.main_pars import ParsSettings
from states.states import GetTrack

user_private_router = Router()

pars_settings = ParsSettings()
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


# Get My tracks
@user_private_router.message(F.text.lower() == "мои треки")
async def get_my_tracks(message: Message, session: AsyncSession):
    await message.answer("Мои треки: \n")

    for user_track in await orm_get_user_tracks(session=session, user_id=message.from_user.id):
        await message.answer(f"Описание: {user_track.user_description}\n"
                             f"Трек номер: {user_track.user_track} \n"
                             f"Сервис отслеживания: {user_track.user_delivery_service} \n"
                             f"Регион доставки (если был выбран): {user_track.user_region}",
                             reply_markup=get_callback_btns(btns={
                                 'Изменить': f'change_user_track_{user_track.id}',
                                 'Удалить': f'delete_user_track_{user_track.id}'
                             })
                             )


# Delete track from my tracks
@user_private_router.callback_query(F.data.startswith('delete_user_track_'))
async def delete_user_track(callback: CallbackQuery, session: AsyncSession):
    track_id = callback.data.split("_")[-1]

    await orm_delete_user_track(session=session, track_id=int(track_id))

    await callback.answer("Трек номер удален")
    await callback.message.answer("Трек номер удален из моих треков")


# Change track from my tracks
# TODO: Create this function
@user_private_router.callback_query(F.data.startswith('change_user_track_'))
async def change_user_track(callback: CallbackQuery, session: AsyncSession):
    track_id = callback.data.split("_")[-1]

    await callback.message.answer("Сработала функция изменения трека")


# Add track in my tracks
@user_private_router.message(F.text.lower() == "добавить трек в 'мои треки'")
@user_private_router.message(StateFilter(None))
async def add_track_in_my_tracks(message: Message, state: FSMContext):
    get_track_states.user_add_track = True
    await message.answer("Введите описание трек номера, например чехол для телефона",
                         reply_markup=skip_keyboard)

    # Go to get track description #
    await state.set_state(get_track_states.user_description)


# Get user description
@user_private_router.message(get_track_states.user_description, or_f(F.text, F.text == "Пропустить поле"))
async def get_user_description(message: Message, state: FSMContext):
    if message.text == "Пропустить поле":
        await state.update_data(user_description="Описание не добавлено")

    else:
        await state.update_data(user_description=message.text.title())

    await message.answer("Выберите где вы хотите отслеживать посылку",
                         reply_markup=choose_track_website_keyboard)

    # Go to get user's delivery service state #
    await state.set_state(get_track_states.user_delivery_service)


# User press track mail
@user_private_router.message(F.text.lower() == "отследить посылку")
@user_private_router.message(StateFilter(None))
async def track(message: Message, state: FSMContext):
    await message.answer("Выберите где вы хотите отслеживать посылку",
                         reply_markup=choose_track_website_keyboard)

    # Go to get user's delivery service state #
    await state.set_state(get_track_states.user_delivery_service)


# Get user's delivery service
@user_private_router.message(get_track_states.user_delivery_service, F.text)
async def get_user_delivery_service(message: Message, state: FSMContext):
    await state.update_data(user_delivery_service=message.text.lower())
    print(message.text.lower())

    if message.text.lower() not in pars_settings.allowed_developing_services:
        await message.answer(pars_settings.unknown_developer_service,
                             reply_markup=choose_track_website_keyboard)

        return

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
    if message.text.lower() not in pars_settings.allowed_tracking_regions:
        await message.answer(pars_settings.unknown_developer_region,
                             reply_markup=choose_delivery_region_keyboard)

        return

    await state.update_data(user_delivery_region=message.text.lower())
    print(message.text.lower())

    await message.answer("Введите трек номер: ",
                         reply_markup=cancel_keyboard)
    # Go to get user's track state #
    await state.set_state(get_track_states.user_track)


# Get user's track
@user_private_router.message(get_track_states.user_track, F.text)
async def get_user_track(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(user_track=message.text.lower())
    print(f"User track: {message.text.lower()}")

    get_data = await state.get_data()
    user_delivery_service = get_data.get("user_delivery_service")
    user_region = get_data.get("user_delivery_region")
    user_track = get_data.get("user_track")

    data = get_track_data_for_user(
        user_url=user_delivery_service,
        user_track_region=user_region,
        user_tracking_numbers=user_track)

    print("printing data in user handler", data)

    if data.get("error"):
        error = data.get("error")
        print(error)
        await message.answer(error,
                             reply_markup=cancel_keyboard)

        return

    else:
        if get_track_states.user_add_track:
            await orm_add_user_track(session=session, data=get_data, message=message)

            await message.answer("Трек номер добавлен в 'мои треки'",
                                 reply_markup=main_keyboard)

        elif not get_track_states.user_track:
            print("Track title: (in user_handler)", data.get("track_title"))

            await message.answer(f"{data.get("track_title")}\n"
                                 f"{data.get("track_numbers")}\n"
                                 f"{data.get("track_location")}\n"
                                 f"{data.get("track_status")}\n"
                                 f"{data.get("track_info_title")}\n"
                                 f"{data.get("track_info_description")}",
                                 reply_markup=main_keyboard)

    await state.clear()
    get_track_states.user_add_track = False
