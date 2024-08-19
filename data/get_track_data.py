from data.parsing.main_pars import GetTrackData


def get_track_data_for_user(user_url: str,
                            user_track_region: str,
                            user_tracking_numbers: str):
    track_data = GetTrackData()
    track_data.get_track_data(user_url=user_url,
                              user_track_region=user_track_region,
                              user_tracking_numbers=user_tracking_numbers)

    return track_data.user_data


# user_url_input = str("почта россии")
# user_track_region_input = str("международный")
# user_tracking_numbers_input = str("ZA278134867CN")
#
# data = get_track_data_for_user(
#     user_url=user_url_input,
#     user_track_region=user_track_region_input,
#     user_tracking_numbers=user_tracking_numbers_input)
#
# if "error" in data:
#     print(data.get("error"))
#
# else:
#     title = data.get("track_title")
#     numbers = data.get("track_numbers")
#     location = data.get("track_location")
#     status = data.get("track_status")
#     info_title = data.get("track_info_title")
#     info_description = data.get("track_info_description")
#
#     print("Track title:", title)
#     print("Track numbers:", numbers)
#     print("Track location:", location)
#     print("Track status:", status)
#     print("Track info title:", info_title)
#     print("Track info description:", info_description)

