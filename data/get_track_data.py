from data.parsing.main_pars import GetTrackData


def get_track_data_for_user(user_url: str,
                            user_track_region: str,
                            user_tracking_numbers: str):
    track_data = GetTrackData()
    track_data.get_track_data(user_url=user_url,
                              user_track_region=user_track_region,
                              user_tracking_numbers=user_tracking_numbers)

    return track_data.user_data
