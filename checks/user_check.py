import requests
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def track_number_check(user_track_numbers: str, track_numbers_amount: int):
    print(f"Check, user_track_numbers: {user_track_numbers}, track_numbers_amount: {track_numbers_amount}")

    if len(str(user_track_numbers)) == int(track_numbers_amount):
        print(True)
        return True

    else:
        print(False)
        return False
    