# Aiogram Imports #
from aiogram import F, Router

from aiogram.filters import CommandStart, StateFilter, or_f

from aiogram.fsm.context import FSMContext

from aiogram.types import Message, CallbackQuery

# sqlalchemy Imports #
from sqlalchemy.ext.asyncio import AsyncSession

from checks.user_check import track_number_check, track_already_in_db
# My Imports #

# keyboards
from keyboards.inline import get_callback_btns

from keyboards.reply import main_keyboard, choose_track_website_keyboard, choose_delivery_region_keyboard, \
    cancel_keyboard, skip_keyboard, cancel_back_skip_keyboard, change_track_website_keyboard, \
    change_delivery_region_keyboard

# data
from data.parsing.main_pars import ParsSettings
from data.get_track_data import get_track_data_for_user

# db
from database.orm_query import orm_get_user_tracks, orm_delete_user_track, orm_add_user_track, orm_get_user_track, \
    orm_get_track_id, orm_update_track

# states
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


# Back function
@user_private_router.message(StateFilter('*'), F.text == "Изменить предыдущее поле")
async def back_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == GetTrack.user_description:
        await message.answer("Предыдущего шага нет\n"
                             "Введите название мероприятия или нажмите 'отмена' ")
        return

    previous_state = None
    for step in GetTrack.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_state.state)
            await message.answer(f"Вы вернулись к предыдущему шагу\n"
                                 f"{GetTrack.texts[previous_state.state]}")
            return
        previous_state = step


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
                                 'Отследить': f'track_user_track_{user_track.id}',
                                 'Изменить': f'change_user_track_{user_track.id}',
                                 'Удалить': f'delete_user_track_{user_track.id}'
                             })
                             )


# Track selected track from my track
@user_private_router.callback_query(F.data.startswith('track_user_track_'))
async def track_user_track(callback: CallbackQuery, session: AsyncSession):
    track_id = callback.data.split("_")[-1]

    user_track = await orm_get_user_track(session=session, track_id=int(track_id))

    data = get_track_data_for_user(
        user_url=user_track.user_delivery_service,
        user_track_region=user_track.user_region,
        user_tracking_numbers=user_track.user_track)

    await callback.message.answer(f"{data.get("track_title")}\n"
                                  f"{data.get("track_numbers")}\n"
                                  f"{data.get("track_location")}\n"
                                  f"{data.get("track_status")}\n"
                                  f"{data.get("track_info_title")}\n"
                                  f"{data.get("track_info_description")}",
                                  reply_markup=main_keyboard)


# Delete track from my tracks
@user_private_router.callback_query(F.data.startswith('delete_user_track_'))
async def delete_user_track(callback: CallbackQuery, session: AsyncSession):
    track_id = callback.data.split("_")[-1]

    track_number = await orm_get_track_id(session=session, track_id=int(track_id))

    await orm_delete_user_track(session=session, track_id=int(track_id))

    await callback.answer("Трек номер удален")
    await callback.message.answer(f"Трек номер {track_number.user_description} ({track_number.user_track}) "
                                  f"удален из моих треков")


# Change track from my tracks
@user_private_router.callback_query(StateFilter(None), F.data.startswith('change_user_track_'))
async def change_user_track(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    track_id = callback.data.split("_")[-1]
    track_for_change = await orm_get_track_id(session=session, track_id=int(track_id))
    get_track_states.track_for_change = track_for_change

    await callback.message.answer("Измените описание трека: ",
                                  reply_markup=cancel_back_skip_keyboard)

    await state.set_state(get_track_states.user_description)


# Add track in my tracks
@user_private_router.message(StateFilter(None), F.text == "Добавить трек в 'мои треки'")
async def add_track_in_my_tracks(message: Message, state: FSMContext):
    print("add_track_in_my_tracks FUNCTION")
    get_track_states.user_add_track = True

    if get_track_states.track_for_change:
        await message.answer("Введите описание трек номера, например чехол для телефона",
                             reply_markup=skip_keyboard)

    else:
        await message.answer("Введите описание трек номера, например чехол для телефона")

    # Go to get track description #
    await state.set_state(get_track_states.user_description)


# Get user description
@user_private_router.message(get_track_states.user_description, or_f(F.text, F.text == "Пропустить поле"))
async def get_user_description(message: Message, state: FSMContext):
    print("get_user_description FUNCTION")
    if message.text == "Пропустить поле":
        if get_track_states.track_for_change is None:  # If user not changing track and want just skip description
            await state.update_data(user_description="Описание не добавлено")
            await message.answer("Выберите где вы хотите отслеживать посылку",
                                 reply_markup=change_track_website_keyboard)

        elif get_track_states.track_for_change:  # If user changing track and want leave same value
            await state.update_data(user_description=get_track_states.track_for_change.user_description)
            await message.answer("Описание не изменено")

            await message.answer("Выберите где вы хотите отслеживать посылку",
                                 reply_markup=change_track_website_keyboard)

    else:
        await state.update_data(user_description=message.text.title())
        if get_track_states.track_for_change:
            await message.answer("Выберите где вы хотите отслеживать посылку",
                                 reply_markup=change_track_website_keyboard)

        elif not get_track_states.track_for_change:
            await message.answer("Выберите где вы хотите отслеживать посылку",
                                 reply_markup=choose_track_website_keyboard)

    # Go to get user's delivery service state #
    await state.set_state(get_track_states.user_delivery_service)


# User press track mail
@user_private_router.message(StateFilter(None), F.text == "Отследить посылку")
async def track(message: Message, state: FSMContext):
    print("track FUNCTION")
    await message.answer("Выберите где вы хотите отслеживать посылку",
                         reply_markup=choose_track_website_keyboard)

    # Go to get user's delivery service state #
    await state.set_state(get_track_states.user_delivery_service)


# Get user's delivery service
@user_private_router.message(get_track_states.user_delivery_service, or_f(F.text, F.text == "Пропустить поле"))
async def get_user_delivery_service(message: Message, state: FSMContext):
    if message.text == "Пропустить поле":
        await state.update_data(user_delivery_service=get_track_states.track_for_change.user_delivery_service)

        if get_track_states.track_for_change.user_delivery_service.lower() == "почта россии":
            # Go to get user's delivery region state #
            await state.set_state(get_track_states.user_delivery_region)
            await message.answer("Служба доставки не изменена",
                                 reply_markup=change_delivery_region_keyboard)
            await message.answer("Выберите регион доставки\n"
                                 "Это нужно, чтобы проверить Ваш трек, у почты россии есть стандарты трек номеров\n\n"
                                 "Трек-номер отправлений по России состоит из 14 цифр. Его вводят без пробелов и "
                                 "скобок —"
                                 "например, 45005145009749.\n"
                                 "Трек-номер международных отправлений состоит из 13 символов, в нём используются "
                                 "латинские заглавные буквы и цифры. Его также вводят без пробелов и скобок — например,"
                                 "CA123466789RU.")

        else:
            await message.answer("Служба доставки не изменена")
            # Go to get user's track state #
            await state.set_state(get_track_states.user_track)
            await message.answer("Введите трек номер: ")

    else:
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
                                 "Трек-номер отправлений по России состоит из 14 цифр. Его вводят без пробелов и "
                                 "скобок —"
                                 "например, 45005145009749.\n"
                                 "Трек-номер международных отправлений состоит из 13 символов, в нём используются "
                                 "латинские заглавные буквы и цифры. Его также вводят без пробелов и скобок — например,"
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
@user_private_router.message(get_track_states.user_delivery_region, or_f(F.text, F.text == "Пропустить поле"))
async def get_user_delivery_region(message: Message, state: FSMContext):
    if message.text == "Пропустить поле":
        if get_track_states.track_for_change is not None:  # If user changing track and want leave same value
            await state.update_data(user_delivery_region=get_track_states.track_for_change.user_region)
            await message.answer("Регион доставки не изменен")
            await message.answer("Введите трек номер: ",
                                 reply_markup=cancel_back_skip_keyboard)

    else:
        if message.text.lower() not in pars_settings.allowed_tracking_regions:
            await message.answer(pars_settings.unknown_developer_region,
                                 reply_markup=choose_delivery_region_keyboard)

            return

        await state.update_data(user_delivery_region=message.text.lower())

        if message.text.lower() == str("россия"):
            await state.update_data(numbers_amount=int(14))

        elif message.text.lower() == str("международный"):
            await state.update_data(numbers_amount=int(13))

        print(message.text.lower())

        await message.answer("Введите трек номер: ",
                             reply_markup=cancel_keyboard)

    # Go to get user's track state #
    await state.set_state(get_track_states.user_track)


# Get user's track
@user_private_router.message(get_track_states.user_track, or_f(F.text, F.text == "Пропустить поле"))
async def get_user_track(message: Message, state: FSMContext, session: AsyncSession):
    # TODO: do some refactoring
    if message.text == "Пропустить поле":
        if get_track_states.track_for_change is not None:  # If user changing track and want leave same value
            await state.update_data(user_track=get_track_states.track_for_change.user_track)
            await message.answer("Трек не изменен")

            track_id = get_track_states.track_for_change.id
            data = await state.get_data()

            # Update track data
            await orm_update_track(session=session, track_id=int(track_id), data=data)
            await message.answer("Данные трек номера изменены!\n"
                                 f"{data.get("user_track")}\n"
                                 f"{data.get("user_description")}\n"
                                 f"{data.get("user_delivery_service")}\n"
                                 f"{data.get("user_delivery_region")}\n",
                                 reply_markup=main_keyboard)

    else:
        await state.update_data(user_track=message.text.lower())
        print(f"User track: {message.text.lower()}")

        get_data = await state.get_data()

        if not track_number_check(user_track_numbers=str(get_data.get("user_track")),
                                  track_numbers_amount=get_data.get("numbers_amount")):

            await message.answer(pars_settings.track_number_error,
                                 reply_markup=cancel_keyboard)
            return

        else:
            if get_track_states.user_add_track:
                if await track_already_in_db(track_number=str(get_data.get("user_track")),
                                             user_id=message.from_user.id, session=session):
                    await message.answer("Данный трек номер уже занесен в ваши треки\n"
                                         "Введите другой трек номер или нажмите 'отмена'")

                    return

                else:
                    await orm_add_user_track(session=session, data=get_data, message=message)

                    await message.answer("Трек номер добавлен в 'мои треки'",
                                         reply_markup=main_keyboard)

            elif not get_track_states.user_add_track:
                data = get_track_data_for_user(
                    user_url=get_data.get("user_delivery_service"),
                    user_track_region=get_data.get("user_delivery_region"),
                    user_tracking_numbers=get_data.get("user_track"))

                print("printing data in user handler", data)

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
    get_track_states.track_for_change = None
