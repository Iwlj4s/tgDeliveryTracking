from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import UserTrackORM


async def track_number_check(user_track_numbers: str):
    print(f"Check, user_track_numbers: {user_track_numbers}")

    if len(str(user_track_numbers)) >= 6:
        print(True)
        return True

    else:
        print(False)
        return False


async def track_already_in_db(track_number: str, user_id: int, session: AsyncSession):
    user_tracks = await UserTrackORM.get_user_id(session=session, user_id=int(user_id))
    print(user_tracks)

    for track in user_tracks:
        print(track.user_track)
        if track.user_track == track_number:
            print(track.user_track)
            return True

    print("No same track in db")
    return False
