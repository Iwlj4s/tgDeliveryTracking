# Aiogram Imports #
from aiogram import F, Router

from aiogram.filters import CommandStart, StateFilter, or_f

from aiogram.fsm.context import FSMContext

from aiogram.types import Message, CallbackQuery

# sqlalchemy Imports #
from sqlalchemy.ext.asyncio import AsyncSession


# My Imports #

# checks
from checks.user_check import track_number_check, track_already_in_db

# keyboards
from keyboards.inline import get_callback_btns

from keyboards.reply import main_keyboard, cancel_keyboard, skip_keyboard, cancel_back_skip_keyboard,  back_keyboard

# data
from data.parsing.main_pars import ParsSettings
from data.get_track_data import get_track_data_for_user

# db
from database.orm_query import UserTrackORM

# states
from states.states import GetTrack

user_private_router = Router()

pars_settings = ParsSettings()
get_track_states = GetTrack()


# Start
@user_private_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Данный бот позволяет отслеживать посылки\n"
                         f"Отслеживайте посылки с Почты России, Украины, Беларуси, Казахстана, "
                         f"Китая, Гонконга, AliExpress, JD, Joom, Pandao, GearBest, Ebay, TaoBao\n\n"
                         f"Для отслеживания используется сайт - https://1track.ru/ \n",
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

    if current_state == get_track_states.user_description:
        await message.answer("Предыдущего шага нет\n"
                             "Введите название мероприятия или нажмите 'отмена' ")
        return

    previous_state = None
    for step in GetTrack.__all_states__:
        if step.state == current_state:
            print(f"Current state: {previous_state.state}")
            await state.set_state(previous_state.state)
            current_keyboard = main_keyboard

            if previous_state.state == get_track_states.user_description:
                current_keyboard = skip_keyboard

            elif previous_state.state == get_track_states.user_track:
                current_keyboard = back_keyboard

            await message.answer(f"Вы вернулись к предыдущему шагу\n"
                                 f"{get_track_states.texts[previous_state.state]}",
                                 reply_markup=current_keyboard)
            return
        previous_state = step


# Get My tracks
@user_private_router.message(F.text.lower() == "мои треки")
async def get_my_tracks(message: Message, session: AsyncSession):
    await message.answer("Мои треки: \n")

    for user_track in await UserTrackORM.get_user_tracks(session=session, user_id=message.from_user.id):
        await message.answer(f"Описание: {user_track.user_description}\n"
                             f"Трек номер: {user_track.user_track} \n",
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

    await callback.message.answer("Получаем данные о посылке...")
    user_track = await UserTrackORM.get_user_track(session=session, track_id=int(track_id))

    track_data = await get_track_data_for_user(user_tracking_numbers=str(user_track.user_track).upper())

    if not track_data.user_data.get("error"):
        await callback.message.answer(
            f"Трек номер: {track_data.track_numbers}\n"
            f"Название предмета: {track_data.track_item_name}\n\n"
            f"Статус трека: {track_data.track_status}\n"
            f"Дата статуса: {track_data.track_status_date}\n\n"
            f"Местоположение: {track_data.track_location}\n"
            f"Отправитель: {track_data.track_sender}\n"
            f"Страна отправителя: {track_data.origin_country}\n\n"
            f"Получатель: {track_data.track_recipient_name}\n"
            f"Страна получателя: {track_data.destination_country}\n"
            f"Адрес получателя: {track_data.track_recipient_address}",
            reply_markup=main_keyboard
        )
    else:
        await callback.message.answer(track_data.user_data["error"],
                                      reply_markup=main_keyboard)


# Delete track from my tracks
@user_private_router.callback_query(F.data.startswith('delete_user_track_'))
async def delete_user_track(callback: CallbackQuery, session: AsyncSession):
    track_id = callback.data.split("_")[-1]

    track_number = await UserTrackORM.get_track_id(session=session, track_id=int(track_id))

    await UserTrackORM.delete_user_track(session=session, track_id=int(track_id))

    await callback.answer("Трек номер удален")
    await callback.message.answer(f"Трек номер {track_number.user_description} ({track_number.user_track}) "
                                  f"удален из моих треков")


# Change track from my tracks
@user_private_router.callback_query(StateFilter(None), F.data.startswith('change_user_track_'))
async def change_user_track(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    track_id = callback.data.split("_")[-1]
    track_for_change = await UserTrackORM.get_track_id(session=session, track_id=int(track_id))
    get_track_states.track_for_change = track_for_change

    await callback.message.answer("Измените описание трека: ",
                                  reply_markup=skip_keyboard)

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
        await message.answer("Введите описание трек номера, например чехол для телефона",
                             reply_markup=skip_keyboard)

    # Go to get track description #
    await state.set_state(get_track_states.user_description)


# Get user description
@user_private_router.message(get_track_states.user_description, or_f(F.text, F.text == "Пропустить поле"))
async def get_user_description(message: Message, state: FSMContext):
    print("get_user_description FUNCTION")
    if message.text == "Пропустить поле":
        if get_track_states.track_for_change is None:  # If user not changing track and want just skip description
            await state.update_data(user_description="Описание не добавлено")
            await message.answer("Введите трек номер",
                                 reply_markup=back_keyboard)

        elif get_track_states.track_for_change:  # If user changing track and want leave same value
            await state.update_data(user_description=get_track_states.track_for_change.user_description)
            await message.answer("Описание не изменено")

            await message.answer("Введите трек номер",
                                 reply_markup=cancel_back_skip_keyboard)

    else:
        await state.update_data(user_description=message.text.title())
        if get_track_states.track_for_change:
            await message.answer("Введите трек номер",
                                 reply_markup=cancel_back_skip_keyboard)

        elif not get_track_states.track_for_change:
            await message.answer("Введите трек номер",
                                 reply_markup=back_keyboard)

    # Go to get user's delivery service state #
    await state.set_state(get_track_states.user_track)


# User press track mail
@user_private_router.message(StateFilter(None), F.text == "Отследить посылку")
async def track(message: Message, state: FSMContext):
    print("track FUNCTION")
    await message.answer("Введите трек номер: ",
                         reply_markup=cancel_keyboard)

    # Go to get user's delivery service state #
    await state.set_state(get_track_states.user_track)


# Get user's track
@user_private_router.message(get_track_states.user_track, or_f(F.text, F.text == "Пропустить поле"))
async def get_user_track(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == "Пропустить поле":
        if get_track_states.track_for_change is not None:  # If user changing track and want leave same value
            await state.update_data(user_track=get_track_states.track_for_change.user_track)
            await message.answer("Трек не изменен")

            track_id = get_track_states.track_for_change.id
            data = await state.get_data()

            await message.answer("Изменяем данные трека номера...")

            # Update track data
            await UserTrackORM.update_track(session=session, track_id=int(track_id), data=data)
            await message.answer("Данные трек номера изменены!\n"
                                 f"{data.get("user_track")}\n"
                                 f"{data.get("user_description")}\n",
                                 reply_markup=main_keyboard)

    else:
        await state.update_data(user_track=message.text.lower())
        print(f"User track: {message.text.lower()}")

        get_data = await state.get_data()

        # track number check
        if not await track_number_check(user_track_numbers=str(get_data.get("user_track"))):
            await message.answer(pars_settings.track_number_error, reply_markup=cancel_keyboard)
            return

        else:
            if get_track_states.user_add_track:
                if await track_already_in_db(track_number=str(get_data.get("user_track")),
                                             user_id=message.from_user.id, session=session):
                    await message.answer("Данный трек номер уже занесен в ваши треки\n"
                                         "Введите другой трек номер или нажмите 'отмена'")
                    return

                else:
                    await message.answer("Добавляем трек в 'мои треки'...")
                    await UserTrackORM.add_user_track(session=session, data=get_data, message=message)

                    await message.answer("Трек номер добавлен в 'мои треки'",
                                         reply_markup=main_keyboard)

            elif not get_track_states.user_add_track:
                await message.answer("Получаем данные о посылке...")

                track_data = \
                    await get_track_data_for_user(user_tracking_numbers=str(get_data.get("user_track").upper()))

                if not track_data.user_data.get("error"):
                    await message.answer(
                        f"Трек номер: {track_data.track_numbers}\n"
                        f"Название предмета: {track_data.track_item_name}\n\n"
                        f"Статус трека: {track_data.track_status}\n"
                        f"Дата статуса: {track_data.track_status_date}\n\n"
                        f"Местоположение: {track_data.track_location}\n"
                        f"Отправитель: {track_data.track_sender}\n"
                        f"Страна отправителя: {track_data.origin_country}\n\n"
                        f"Получатель: {track_data.track_recipient_name}\n"
                        f"Страна получателя: {track_data.destination_country}\n"
                        f"Адрес получателя: {track_data.track_recipient_address}",
                        reply_markup=main_keyboard
                    )
                else:
                    await message.answer(track_data.user_data["error"],
                                         reply_markup=main_keyboard)

    await state.clear()
    get_track_states.user_add_track = False
    get_track_states.track_for_change = None
