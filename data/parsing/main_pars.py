import requests
import logging
import time
import sys
import os
import aiohttp

from bs4 import BeautifulSoup

# My Imports #
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from checks.user_check import track_number_check

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParsSettings:
    def __init__(self) -> None:
        self.pochta_ru_url = "https://www.pochta.ru/tracking"  # "Pochta ru" tracking web site
        # self.seventeen_track_url = "https://m.17track.net/ru/"  # 17Track tracking website

        self.search_url = ""
        self.search_query = ""

        self.allowed_developing_services = ["почта россии"]
        self.allowed_tracking_regions = ["россия", "международный"]

        self.user_tracking_url = None

        self.user_track_input = None
        self.user_track_find_button = None

        self.pochta_ru_tracking_region = None  # If region == Russia -> track number consist of 14 digits, if region
        # == International -> track number consist of 13 characters

        # !! International track has digits AND characters !! #
        self.pochta_ru_tracking_numbers_amount = None

        self.user_tracking_numbers = ""

        self.user_data = {}

        self.unknown_developer_service = str("Неизвестная служба доставки\n"
                                             "Пожалуйста выберите службу доставки из списка в кнопочном меню")
        self.unknown_developer_region = str("Неизвестный регион доставки\n"
                                            "Пожалуйста выберите регион доставки из списка в кнопочном меню")

        self.track_number_error = str(
            "Ваш трек номер содержит ошибку, пожалуйста проверьте его.\n"
            "Для отправлений по России трек-номер состоит из 14 цифр.\n"
            "Для международных — из 13 символов, в нём используются латинские заглавные буквы и цифры.\n"
            "\nВведите трек-номер заново")

        self.driver = None
        self.response = None
        self.html = None
        self.soup = None


class GetUserData(ParsSettings):
    def __init__(self):
        super().__init__()
        self.developer_service_error = "Unknown developer service"

        # Getting User's URL #
        # What delivery use?

    async def get_user_url(self, user_url: str):
        user_url = user_url.strip().lower()
        logger.info(f"User inputted url: '{user_url}'")

        if user_url == "почта россии":
            self.user_tracking_url = self.pochta_ru_url
            self.search_url = self.pochta_ru_url + "?barcode="
            logger.info(f"New URL: {self.user_tracking_url}")

        else:
            self.user_tracking_url = ""
            self.search_url = ""
            self.user_data = {"error": self.unknown_developer_service}

            return False

        return self.user_tracking_url

    # Get ! amount ! tracking numbers for Pochta ru #
    # If delivery == Pochta ru -> getting track region (ru / international)
    async def get_user_track_region(self, user_track_region: str) -> str:
        if str(user_track_region) == str("россия").lower():
            self.pochta_ru_tracking_region = str("ru")
            self.pochta_ru_tracking_numbers_amount = int(14)

        elif str(user_track_region) == str("международный").lower():
            self.pochta_ru_tracking_region = str("international")
            self.pochta_ru_tracking_numbers_amount = int(13)

        return self.pochta_ru_tracking_region

    # Getting user tracking numbers
    async def get_user_tracking_numbers(self, user_tracking_numbers: str):
        if track_number_check(user_track_numbers=user_tracking_numbers,
                              track_numbers_amount=self.pochta_ru_tracking_numbers_amount):
            print("In main pars, user_tracking_numbers: ", user_tracking_numbers)
            self.user_tracking_numbers = str(user_tracking_numbers)
            self.search_url = self.search_url + str(self.user_tracking_numbers.upper())
            print("SEARCH URL IN TN", self.search_url)
            return True

        else:
            self.user_tracking_numbers = None
            self.user_data = {"error": self.track_number_error}
            return False


class Parser(GetUserData, ParsSettings):
    async def get_html_page_with_user_track_data(self, user_url: str,
                                                 user_track_region: str,
                                                 user_tracking_numbers: str):
        async with aiohttp.ClientSession() as session:
            self.user_tracking_url = await self.get_user_url(user_url=str(user_url))
            if not self.user_tracking_url:
                return self.user_data.get("error")

            self.get_user_track_region = await self.get_user_track_region(str(user_track_region))

            if not await self.get_user_tracking_numbers(user_tracking_numbers=str(user_tracking_numbers)):
                return self.user_data.get("error")

            print("SEARCH URL IN SESSION: ", self.search_url)

            async with session.get(self.search_url) as response:
                self.response = response
                self.html = await response.text()

                self.soup = BeautifulSoup(self.html, "lxml")

                return self.soup


class GetTrackData(Parser, ParsSettings):
    def __init__(self) -> None:
        super().__init__()
        self.track_title = None
        self.track_location = None
        self.track_numbers = None
        self.track_status = None
        self.track_info = None
        self.track_info_title = None
        self.track_info_description = None

    # Get Data For Pochta Ru #
    async def get_pochta_ru_data(self):

        # Track title
        self.track_title = self.soup.find('div', class_='hubGBa')
        self.track_title = self.track_title.text if self.track_title else None

        # Track location
        self.track_location = self.soup.find('span', class_='hftVBh')
        self.track_location = self.track_location.text if self.track_location else ""

        # Track numbers
        self.track_numbers = self.soup.find('span', class_='hoxweJ')
        self.track_numbers = self.track_numbers.text.split('<')[0] if self.track_numbers else None

        # Track status
        self.track_status = self.soup.find('span', class_='fYSIwJ')
        self.track_status = self.track_status.text if self.track_status else None

        # Track info
        self.track_info = self.soup.find('div', class_='ccIMJb')
        if self.track_info:
            self.track_info_title = self.track_info.find('p', class_='icMJRk')
            self.track_info_title = self.track_info_title.text if self.track_info_title else None

            self.track_info_description = self.track_info.find('p', class_='gPYwYo')
            self.track_info_description = self.track_info_description.text if self.track_info_description else None

    async def get_track_data(self, user_url: str,
                             user_track_region: str,
                             user_tracking_numbers: str):
        try:
            self.soup = await self.get_html_page_with_user_track_data(
                user_url=str(user_url),
                user_track_region=str(user_track_region),
                user_tracking_numbers=str(user_tracking_numbers)
            )

            if self.soup:

                # Get POCHTA RU data #
                if self.user_tracking_url == self.pochta_ru_url:
                    await self.get_pochta_ru_data()

                    self.user_data = {
                        "track_title": self.track_title,
                        "track_location": self.track_location,
                        "track_numbers": self.track_numbers,
                        "track_status": self.track_status,
                        "track_info_title": self.track_info_title,
                        "track_info_description": self.track_info_description
                    }
                    return self.user_data

                else:
                    print("No pochta ru url")

                logger.info("Response TRACK")
            else:
                logger.error("Can't response HTML")
        except Exception as e:
            logger.error(f"Error response data: {e}")

