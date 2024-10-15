import logging

import aiohttp

# My Imports #
from checks.user_check import track_number_check

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParsSettings:
    def __init__(self) -> None:
        self.one_track_url = "https://1trackapp.com/ajax/tracking?lang=&track="  # 1Track tracking website

        self.search_url = ""

        self.user_tracking_numbers = ""

        self.user_data = {}

        self.response = None

        self.track_number_error = str(
            "Ваш трек номер содержит ошибку, пожалуйста проверьте его.\n"
            "Трек номер должен содержать от 6 символов/цифр, символов И цифр")


class GetUserData(ParsSettings):
    def __init__(self):
        super().__init__()
        self.developer_service_error = "Unknown developer service"

    # Getting user tracking numbers
    async def get_user_tracking_numbers(self, user_tracking_numbers: str):
        if await track_number_check(user_track_numbers=str(user_tracking_numbers)):
            print("In main pars, user_tracking_numbers: ", user_tracking_numbers)
            self.user_tracking_numbers = str(user_tracking_numbers)
            return True

        else:
            self.user_tracking_numbers = None
            self.user_data = {"error": self.track_number_error}
            return False


class Parser(GetUserData, ParsSettings):
    async def get_ajax_track_data(self, user_tracking_numbers: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.one_track_url + user_tracking_numbers + "&new=true") as response:
                print(self.one_track_url + user_tracking_numbers + "&new=true")
                if response.status == 200:
                    self.response = await response.json()
                    print(self.response)


class GetTrackData(Parser, ParsSettings):
    def __init__(self) -> None:
        super().__init__()
        self.track_last_event = None

        self.track_numbers = None
        self.track_item_name = None

        self.track_status = None
        self.track_status_date = None

        self.track_location = None

        self.track_recipient_name = None
        self.track_recipient_address = None

        self.track_sender = None

        self.origin_country = None
        self.destination_country = None

        self.info = None

    async def get_data(self, user_tracking_numbers: str):
        await self.get_user_tracking_numbers(user_tracking_numbers=user_tracking_numbers)
        await self.get_ajax_track_data(user_tracking_numbers=user_tracking_numbers)

        if self.response is not None:
            print(self.response)
            data = self.response.get("data", {})
            if data:
                if data.get("status") == "error" or data.get("status") == "False" or not data.get("status"):
                    error_message = data.get("error", "Неизвестная ошибка")
                    self.user_data = {"error": f"К сожалению, мы не можем отследить этот трек номер: {error_message}"}

                self.track_numbers = data["trackcode"]
                self.track_status = data["status"]

                self.origin_country = data["origin_country"]
                self.destination_country = data["destination_country"]

                self.info = data["info"]

                events = data.get("events", [])
                if events:
                    last_event = events[0]
                    self.track_last_event = last_event
                    self.track_status = last_event["attribute"]
                    self.track_status_date = last_event["date"]

                    event_location = self.track_last_event.get("location")
                    if event_location:
                        self.track_location = event_location["address"]
                    else:
                        self.track_location = "Локация посылки недоступна"

                    self.track_item_name = self.info["ComplexItem"]

                    self.track_sender = self.info["Sender"]
                    self.track_recipient_name = self.info["Recipient"]
                    self.track_recipient_address = self.info["AddressTo"]

                else:
                    self.user_data = {"error": self.track_number_error}

            else:
                self.user_data = {"error": self.track_number_error}
                logger.error("No data found in response")
        else:
            self.user_data = {"error": self.track_number_error}
            logger.error("Response is None, cannot get data")

    async def get_track_data(self, user_tracking_numbers: str):
        try:

            await self.get_data(user_tracking_numbers=user_tracking_numbers)
            if not self.user_data.get("error"):
                self.user_data = {
                    "track_numbers": self.track_numbers,
                    "item_name": self.track_item_name,
                    "track_status": self.track_status,
                    "track_date": self.track_status_date,
                    "track_location": self.track_location,
                    "sender": self.track_sender,
                    "origin_country": self.origin_country,
                    "recipient_name": self.track_recipient_name,
                    "destination_country": self.destination_country,
                    "recipient_address": self.track_recipient_address
                }
                return self.user_data
            else:
                return self.user_data.get("error")

        except Exception as e:
            logger.error(f"Error response data: {e}")
            return self.user_data.get("error")
