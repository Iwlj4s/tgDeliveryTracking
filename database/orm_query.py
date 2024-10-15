from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserTrack


class UserTrackORM:
    @classmethod
    # Add track in my tracks
    async def add_user_track(cls, session: AsyncSession, data: dict, message):
        obj = UserTrack(
            user_tg_id=int(message.from_user.id),
            user_track=data['user_track'],
            user_description=data['user_description']
        )

        session.add(obj)

        await session.commit()

    @classmethod
    # Get trackS
    async def get_user_tracks(cls, session: AsyncSession, user_id: int):
        query = select(UserTrack).where(UserTrack.user_tg_id == int(user_id))
        result = await session.execute(query)

        return result.scalars().all()

    @classmethod
    # Get track
    async def get_user_track(cls, session: AsyncSession, track_id: int):
        query = select(UserTrack).where(UserTrack.id == int(track_id))
        result = await session.execute(query)
        track = result.scalar()

        return track

    @classmethod
    # Get track id
    async def get_track_id(cls, session: AsyncSession, track_id: int):
        query = select(UserTrack).where(UserTrack.id == int(track_id))
        result = await session.execute(query)
        track = result.scalar()

        return track

    @classmethod
    # Get user by id
    async def get_user_id(cls, session: AsyncSession, user_id: int):
        query = select(UserTrack).where(UserTrack.user_tg_id == int(user_id))
        result = await session.execute(query)
        user_tracks = result.scalars().all()

        print(user_tracks)

        return user_tracks

    @classmethod
    # Delete track
    async def delete_user_track(cls, session: AsyncSession, track_id: int):
        query = delete(UserTrack).where(UserTrack.id == int(track_id))
        await session.execute(query)

        await session.commit()

    @classmethod
    # Update track
    async def update_track(cls, session: AsyncSession, track_id: int, data: dict):
        query = update(UserTrack).where(UserTrack.id == int(track_id)).values(
            user_track=data['user_track'],
            user_description=data['user_description']
        )

        await session.execute(query)
        await session.commit()

        print(f"User Track updated successfully.")
