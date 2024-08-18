import requests
import logging
import time
import sys
import os

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

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

        self.user_tracking_url = None

        self.user_track_input = None
        self.user_track_find_button = None

        # I guess I delete this const next time, but for now it's will be here #
        self.pochta_ru_tracking_region = None  # If region == Russia -> track number consist of 14 digits, if region
        # == International -> track number consist of 13 characters

        # !! International track has digits AND characters !! #
        self.pochta_ru_tracking_numbers_amount = None

        self.user_tracking_numbers = None

        self.track_number_error = str(
            "Ваш трек номер содержит ошибку, пожалуйста проверьте его. "
            "\nДля отправлений по России трек-номер состоит из 14 цифр."
            "\n Для международных — из 13 символов, в нём используются латинские заглавные буквы и цифры.")


class Driver(ParsSettings):
    def __init__(self) -> None:
        super().__init__()

        self.chrome_options = Options()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument("--allow-running-insecure-content")
        self.chrome_options.add_argument("--allow-insecure-localhost")
        self.chrome_options.add_argument("--disable-web-security")
        self.chrome_options.add_argument("--incognito")
        # self.chrome_options.add_argument("--auto-open-devtools-for-tabs")  

        # self.chrome_options.add_argument("--headless")  # background start

        self.driver = None
        self.response = None
        self.new_html = None
        self.soup = None

        self.developer_service_error = "Unknown developer service"

    # DRIVER INIT #
    def initialize_driver(self):
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.set_page_load_timeout(30)
            logger.info("WebDriver successfully init")
        except Exception as e:
            logger.error(f"Init Error WebDriver: {e}")
            raise

    # DRIVER QUIT
    def quit_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Close Driver Error: {e}")
            finally:
                self.driver = None

    # Getting User's URL #
    # What delivery use? 
    def get_user_url(self, user_url: str):
        user_url = user_url.strip().lower()
        logger.info(f"User inputted url: '{user_url}'")

        if user_url == "почта россии":
            self.user_tracking_url = self.pochta_ru_url
            logger.info(f"New URL: {self.user_tracking_url}")

        else:
            logger.error(f"Unknown developer service: '{user_url}'")
            return print(self.developer_service_error)

        try:
            if not self.driver:
                self.initialize_driver()
            logger.info(f"Try to open URL: {self.user_tracking_url}")
            self.driver.get(self.user_tracking_url)

            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logger.info("Page successfully load")

        except TimeoutException:
            logger.error("Time out page / components load")
            self.driver.quit()
            return None

        except Exception as e:
            logger.error(f"Page load Error: {e}")
            self.driver.quit()
            return None

        return self.user_tracking_url

    # Load components func
    def load_components(self):
        # If user url = Pochta ru #
        if self.user_tracking_url == self.pochta_ru_url:
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

    # Get ! amount ! tracking numbers for Pochta ru #
    # If delivery == Pochta ru -> getting track region (ru / international)
    def get_user_track_region(self, user_track_region: str) -> str:
        if str(user_track_region) == str("россия").lower():
            self.pochta_ru_tracking_region = str("ru")
            self.pochta_ru_tracking_numbers_amount = int(14)

        elif str(user_track_region) == str("международный").lower():
            self.pochta_ru_tracking_region = str("international")
            self.pochta_ru_tracking_numbers_amount = int(13)

        return self.pochta_ru_tracking_region

    # Getting user tracking numbers
    def get_user_tracking_numbers(self, user_tracking_numbers: str):
        if track_number_check(user_track_numbers=user_tracking_numbers,
                              track_numbers_amount=self.pochta_ru_tracking_numbers_amount):
            print("In main pars, user_tracking_numbers: ", user_tracking_numbers)
            return self.get_user_tracking_numbers == str(user_tracking_numbers)

        else:
            print(str(self.track_number_error))
            return str(self.track_number_error)

    # Enter in input user tracking digits 
    def enter_in_input_tracking_digits(self, user_tracking_numbers: str):
        try:
            # self.user_track_input.clear()
            self.user_track_input.send_keys(user_tracking_numbers)

            time.sleep(3)

            logger.info(f"User inputted TRACK: {user_tracking_numbers}")

            self.user_track_find_button.click()
            logger.info("Search Button")

            time.sleep(3)

        except Exception as e:
            logger.error(f"Track Input Error: {e}")

    # Get new html page with tracking info
    def get_html_page_with_tracking_info(self, user_url: str,
                                         user_track_region: str,
                                         user_tracking_numbers: str):

        # 1. What delivery use? (Pochta ru / 17Track)
        self.user_tracking_url = self.get_user_url(user_url=str(user_url))
        if not self.user_tracking_url:
            logger.error("No URL. Destruct Operation.")

            return None

        # loading input and search button
        self.load_components()

        try:
            self.response = requests.get(self.user_tracking_url)
            logger.info(f"Successfully request to {self.user_tracking_url}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Eror request: {e}")

            return None

        # 2. If delivery == Pochta ru -> geting track region (ru / international)
        self.get_user_track_region = self.get_user_track_region(str(user_track_region))

        # 3. Getting user tracking numbers (Pochta ru / CDEK)
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
        self.track_location = None
        self.track_numbers = None
        self.track_status = None
        self.track_info = None
        self.track_info_title = None
        self.track_info_description = None

    # Get Data For Pochta Ru #
    def get_pochta_ru_data(self):

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

                # Get POCHTA RU data #
                if self.user_tracking_url == self.pochta_ru_url:

                    self.get_pochta_ru_data()

                else:
                    print("No pochta ru url")

                logger.info("Response TRACK")
            else:
                logger.error("Can't response HTML")
        except Exception as e:
            logger.error(f"Error response data: {e}")
        finally:
            self.quit_driver()


def main():
    user_url_input = str("почта россии")
    user_track_region_input = str("международный")
    user_tracking_numbers_input = str("ZA281165674CN")

    track_data = GetTrackData()
    track_data.get_track_data(user_url=user_url_input,
                              user_track_region=user_track_region_input,
                              user_tracking_numbers=user_tracking_numbers_input)

    print("Track title: ", track_data.track_title)
    print("Track numbers: ", track_data.track_numbers)
    print("Track location: ", track_data.track_location)
    print("Track status: ", track_data.track_status)
    print("Track info title: ", track_data.track_info_title)
    print("Track info description: ", track_data.track_info_description)

    track_data.quit_driver()

# main()
