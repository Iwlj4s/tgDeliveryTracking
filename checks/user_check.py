from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_track_id, orm_get_user_id


def track_number_check(user_track_numbers: str, track_numbers_amount: int):
    print(f"Check, user_track_numbers: {user_track_numbers}, track_numbers_amount: {track_numbers_amount}")

    if len(str(user_track_numbers)) == int(track_numbers_amount):
        print(True)
        return True

    else:
        print(False)
        return False


async def track_already_in_db(track_number: str, user_id: int, session: AsyncSession):
    user_tracks = await orm_get_user_id(session=session, user_id=int(user_id))
    print(user_tracks)

    for track in user_tracks:
        print(track.user_track)
        if track.user_track == track_number:
            print(track.user_track)
            return True

    print("No same track in db")
    return False
