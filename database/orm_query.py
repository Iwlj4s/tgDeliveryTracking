from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserTrack


async def orm_add_user_track(session: AsyncSession, data: dict, message):
    obj = UserTrack(
        user_tg_id=int(message.from_user.id),
        user_delivery_service=data['user_delivery_service'],
        user_region=data['user_delivery_region'],
        user_track=data['user_track'],
        user_description=data['user_description']
    )

    session.add(obj)

    await session.commit()


async def orm_get_user_tracks(session: AsyncSession, user_id: int):
    query = select(UserTrack).where(UserTrack.user_tg_id == int(user_id))
    result = await session.execute(query)

    return result.scalars().all()


async def orm_delete_user_track(session: AsyncSession, track_id: int):
    query = delete(UserTrack).where(UserTrack.id == int(track_id))
    await session.execute(query)

    await session.commit()
