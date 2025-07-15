# Telegram Bot for Package Tracking

!!! This project is a Telegram bot that helps users track their packages using data from the "1Track" website (https://1track.ru/). !!!


## Important Note
For now I do not plan to purchase hosting for this project.

## Description
The bot combines a "1Track" parser with a Telegram interface, allowing users to easily get information about their packages through chat. 

It uses <a href="https://selenium-python.readthedocs.io/getting-started.html">aiohttp</a> for web scraping, as well as the Telegram library <a href="aiogram">aiogram</a> for bot functionality.

Users can track their packages without necessarily adding them to the database, but they also have the option to:

- Add a track
- Change a track
- Delete a track


## Main Features
- **Track Packages**: Users can track their packages directly.
- **Add Tracks**: Users have the option to add their tracks to the database.
- **Change and Delete Tracks**: Users can modify or remove their tracks from the database.

- **Database Management**
  - Utilizes  <a href="https://www.sqlalchemy.org/">SQLAlchemy</a> for handling user tracks in the SQLite database.

- **Telegram Bot Interface**
  - Implements an intuitive button-based interface for user interactions.
  - Handles user selections and processes requests.
  - Presents package information in a user-friendly format.

## How It Works
Users start the bot and are presented with the main menu. Based on the user's selection, the bot offers additional options or retrieves package information. Users can track their packages directly, and the bot will provide up-to-date information on the status of each package.
