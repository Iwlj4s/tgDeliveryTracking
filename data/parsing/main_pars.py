import requests
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# My Imports #
from checks.user_check import track_number_check

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParsSettings:
    def __init__(self) -> None:
        self.pochta_ru_url = "https://www.pochta.ru/tracking"  # "Pochta ru" tracking web site
        self.cdek_url = "https://www.cdek.ru/ru/tracking/"  # CDEK tracking web site

        self.user_tracking_url = None

        self.user_track_input = None
        self.user_track_find_button = None

        # I guess I delete this const next time, but for now it's will be here #
        self.pochta_ru_tracking_region = None  # If region == Russia -> track number consist of 14 digits, if region == International -> track number consist of 13 characters

        # !! International track has digits AND charackters !! #
        self.pochta_ru_tracking_numbers_amount = None

        self.user_tracking_numbers = None

        self.track_number_error = str(
            "Ваш трек номер содержит ошибку, пожалуйста проверьте его. "
            "\nДля отправлений по России трек-номер состоит из 14 цифр."
            "\n Для международных — из 13 символов, в нём используются латинские заглавные буквы и цифры.")


class Driver(ParsSettings):
    def __init__(self) -> None:
        super().__init__()

        self.driver = None
        self.new_html = None
        self.soup = None

        self.developer_service_error = "Unknow developer service"

    def initialize_driver(self):
        try:
            self.driver = webdriver.Chrome()
            self.driver.set_page_load_timeout(30)
            logger.info("WebDriver successfully init")
        except Exception as e:
            logger.error(f"Init Error WebDriver: {e}")
            raise

    def quit_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Clsoe Driver Error: {e}")
            finally:
                self.driver = None

    # Getting User's URL #
    # 1. What delivery use? (Pochta ru / CDEK)
    def get_user_url(self, user_url: str) -> str:
        user_url = user_url.strip().lower()  # Удаляем пробелы и приводим к нижнему регистру
        logger.info(f"User inputed url: '{user_url}'")

        if user_url == "почта россии":
            self.user_tracking_url = self.pochta_ru_url
            logger.info(f"New URL: {self.user_tracking_url}")

        elif user_url == "сдэк":
            self.user_tracking_url = self.cdek_url
            logger.info(f"New URL: {self.user_tracking_url}")

        else:
            logger.error(f"Unknow developer service: '{user_url}'")
            return print(self.developer_service_error)
        
        try:
            if not self.driver:
                self.initialize_driver()
            logger.info(f"Try to open URL: {self.user_tracking_url}")
            self.driver.get(self.user_tracking_url)

            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logger.info("Page successfully load")

            # Wait Input
            self.user_track_input = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, "tracking-toolbar__search-input"))
            )
            logger.info("Input find")

            # Wait search button
            self.user_track_find_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='tracking.search-button']"))
            )
            logger.info("Button find")

        except TimeoutException:
            logger.error("Time out page / components load")
            self.driver.quit()
            return None

        except Exception as e:
            logger.error(f"Page load Error: {e}")
            self.driver.quit()
            return None

        return self.user_tracking_url

    # Get ! amount ! tracking numbers for Pochta ru #
    # 2. If delivery == Pochta ru -> geting track region (ru / international)
    def get_user_track_region(self, user_track_region: str) -> str:
        if str(user_track_region) == str("россия").lower():
            self.pochta_ru_tracking_region = str("ru")
            self.pochta_ru_tracking_numbers_amount = int(14)

        elif str(user_track_region) == str("международный").lower():
            self.pochta_ru_tracking_region = str("international")
            self.pochta_ru_tracking_numbers_amount = int(13)

        return self.pochta_ru_tracking_region

    # 3. Geting user tracking numbers (Pochta ru / CDEK)     
    def get_user_tracking_numbers(self, user_tracking_numbers: str) -> str:
        if track_number_check(user_track_numbers=user_tracking_numbers,
                              track_numbers_amount=self.pochta_ru_tracking_numbers_amount):
            print("In main pars, user_tracking_numbers: ", user_tracking_numbers)
            return self.get_user_tracking_numbers == str(user_tracking_numbers)

        else:
            print(str(self.track_number_error))
            return str(self.track_number_error)

    # 4. Enter in input user tracking digits 
    def enter_in_input_tracking_digits(self, user_tracking_numbers: str):
        try:
            self.user_track_input.clear()
            self.user_track_input.send_keys(user_tracking_numbers)
            logger.info(f"User inputed TRACK: {user_tracking_numbers}")

            self.user_track_find_button.click()
            logger.info("Search Button")

            time.sleep(5)

        except Exception as e:
            logger.error(f"Track Input Error: {e}")

    # 5. Get new html page with tracking info
    def get_html_page_with_tracking_info(self, user_url: str,
                                         user_track_region: str,
                                         user_tracking_numbers: str):

        # 1. What delivery use? (Pochta ru / CDEK)
        self.user_tracking_url = self.get_user_url(user_url=str(user_url))
        if not self.user_tracking_url:
            logger.error("No URL. Destruct Operation.")

            return None

        try:
            self.response = requests.get(self.user_tracking_url)
            logger.info(f"Successfully request to {self.user_tracking_url}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Eror request: {e}")

            return None

        # 2. If delivery == Pochta ru -> geting track region (ru / international)
        self.get_user_track_region = self.get_user_track_region(str(user_track_region))

        # 3. Geting user tracking numbers (Pochta ru / CDEK) 
        self.get_user_tracking_numbers(user_tracking_numbers=str(user_tracking_numbers))

        # 4. Enter in input user tracking digits 
        self.enter_in_input_tracking_digits(user_tracking_numbers=user_tracking_numbers)

        time.sleep(3)

        # 5. Get new HTML content

        self.new_html = self.driver.page_source
        self.soup = BeautifulSoup(self.new_html, "lxml")

        self.quit_driver()

        return self.soup


class GetTrackData(Driver, ParsSettings):
    def __init__(self) -> None:
        super().__init__()
        self.track_title = None
        self.track_numbers = None
        self.track_status = None
        self.track_info = None
        self.track_info_title = None
        self.track_info_description = None

    def get_track_data(self, user_url: str,
                       user_track_region: str,
                       user_tracking_numbers: str):
        try:
            self.soup = self.get_html_page_with_tracking_info(
                user_url=str(user_url),
                user_track_region=str(user_track_region),
                user_tracking_numbers=str(user_tracking_numbers)
            )

            if self.soup:
                self.track_title = self.soup.find('div', class_='hubGBa')
                self.track_title = self.track_title.text if self.track_title else None

                self.track_numbers = self.soup.find('span', class_='hoxweJ')
                self.track_numbers = self.track_numbers.text.split('<')[0] if self.track_numbers else None

                self.track_status = self.soup.find('span', class_='fYSIwJ')
                self.track_status = self.track_status.text if self.track_status else None

                self.track_info = self.soup.find('div', class_='ccIMJb')
                if self.track_info:
                    self.track_info_title = self.track_info.find('p', class_='icMJRk')
                    self.track_info_title = self.track_info_title.text if self.track_info_title else None

                    self.track_info_description = self.track_info.find('p', class_='gPYwYo')
                    self.track_info_description = self.track_info_description.text if self.track_info_description else None

                logger.info("Response TRACK")
            else:
                logger.error("Can't response HTML")
        except Exception as e:
            logger.error(f"Error response data: {e}")
        finally:
            self.quit_driver()


def main():
    user_url_input = str("почта россии")
    user_track_region_input = str("россия")
    user_tracking_numbers_input = str("14598787026595")

    track_data = GetTrackData()
    track_data.get_track_data(user_url=user_url_input,
                              user_track_region=user_track_region_input,
                              user_tracking_numbers=user_tracking_numbers_input)

    print("Track title: ", track_data.track_title)
    print("Track numbers: ", track_data.track_numbers)
    print("Track status: ", track_data.track_status)
    print("Track info title: ", track_data.track_info_title)
    print("Track info description: ", track_data.track_info_description)

    track_data.quit_driver()


main()
