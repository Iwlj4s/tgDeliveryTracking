from data.parsing.main_pars import GetTrackData


def get_track_data_for_user(user_url: str,
                            user_track_region: str,
                            user_tracking_numbers: str):
    track_data = GetTrackData()
    track_data.get_track_data(user_url=user_url,
                              user_track_region=user_track_region,
                              user_tracking_numbers=user_tracking_numbers)

    return track_data.user_data


async def main():
    user_url_input = str("почта россии")
    user_track_region_input = str("россия")
    user_tracking_numbers_input = str("14598787026595")

    track_data = GetTrackData()
    await track_data.get_track_data(user_url=user_url_input,
                              user_track_region=user_track_region_input,
                              user_tracking_numbers=user_tracking_numbers_input)

    if user_url_input == "17track":
        print("Track title: ", track_data.track_title)
        print("Track numbers: ", track_data.track_numbers)
        print("Track status: ", track_data.track_status)
        print("Track info : ", track_data.track_info)

    elif user_url_input == "почта россии":
        print("Track title: ", track_data.track_title)
        print("Track numbers: ", track_data.track_numbers)
        print("Track status: ", track_data.track_status)
        print("Track info title: ", track_data.track_info_title)
        print("Track info description: ", track_data.track_info_description)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
