from data.parsing.main_pars import GetTrackData


async def get_track_data_for_user(user_tracking_numbers: str):
    track_data = GetTrackData()
    await track_data.get_track_data(user_tracking_numbers=user_tracking_numbers)

    return track_data.user_data


async def main():
    user_tracking_numbers_input = str("ZA271313095CN")

    track_data = GetTrackData()
    await track_data.get_track_data(user_tracking_numbers=str(user_tracking_numbers_input))

    if not track_data.user_data.get("error"):
        print("Track numbers: ", track_data.track_numbers)
        print("Track item_name: ", track_data.track_item_name)
        print("Track status: ", track_data.track_status)
        print("Track status date: ", track_data.track_status_date)
        print("Track location ", track_data.track_location)
        print("Track sender ", track_data.track_sender)
        print("Origin country ", track_data.origin_country)
        print("Recipient name: ", track_data.track_recipient_name)
        print("Recipient country: ", track_data.destination_country)
        print("Recipient address: ", track_data.track_recipient_address)
    else:
        print("Error: ", track_data.user_data["error"])

if __name__ == '__main__':
    import asyncio

    asyncio.run(main())