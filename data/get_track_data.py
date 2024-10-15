from data.parsing.main_pars import GetTrackData


async def get_track_data_for_user(user_tracking_numbers: str):
    track_data = GetTrackData()
    await track_data.get_track_data(user_tracking_numbers=str(user_tracking_numbers))

    return track_data
