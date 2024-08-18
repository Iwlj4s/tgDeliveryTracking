from data.parsing.main_pars import GetTrackData


def get_track_data_for_user(user_url: str,
                            user_track_region: str,
                            user_tracking_numbers: str):
    track_data = GetTrackData()
    track_data.get_track_data(user_url=user_url,
                              user_track_region=user_track_region,
                              user_tracking_numbers=user_tracking_numbers)

    track_title = track_data.track_title
    track_numbers = track_data.track_numbers
    track_location = track_data.track_location

    track_status = track_data.track_status
    track_info_title = track_data.track_info_title
    track_info_description = track_data.track_info_description

    print("Track title (in get_track_data file): ", track_title)
    print("Track numbers (in get_track_data file): ", track_numbers)
    print("Track location (in get_track_data file): ", track_location)
    print("Track status (in get_track_data file): ", track_status)
    print("Track info title (in get_track_data file): ", track_info_title)
    print("Track info description (in get_track_data file): ", track_info_description)

    return track_title, track_numbers, track_location, track_status, track_info_title, track_info_description


user_url_input = str("почта россии")
user_track_region_input = str("международный")
user_tracking_numbers_input = str("ZA281165674CN")

# (track_title, track_numbers,
#  track_location,
#  track_status,
#  track_info_title,
#  track_info_description) = get_track_data_for_user(
#     user_url=user_url_input,
#     user_track_region=user_track_region_input,
#     user_tracking_numbers=user_tracking_numbers_input)
#
# print("Track title: ", track_title)
# print("Track numbers: ", track_numbers)
# print("Track: ", track_location)
# print("Track status: ", track_status)
# print("Track info title: ", track_info_title)
# print("Track info description: ", track_info_description)
