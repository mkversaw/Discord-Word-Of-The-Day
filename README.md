# Word of the Day (self) Bot

A script for discord that will update an account's status with the Word of the Day pulled from a CSV file.
This script can be run using a bot or user token depending on your needs.

## Features
- Sets a daily Word of the Day as the account's custom status.
- Words are sourced from a CSV file, with support for year-specific word lists.
- Runs automatically at a specified time using a scheduling library.

## Requirements
- Python 3.8 or newer
- A Discord token
  - Either a bot token or a user token. See the discord developer documentation for details on obtaining tokens.
- A CSV file containing the words for each day of the year
  - A sample file is included for getting started.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/discord-word-of-the-day.git
   cd discord-word-of-the-day
   ```
2. **Install dependencies**:
    ```bash
    pip install discord.py schedule discord.py-self
    ```

4. **Set up the environment file**: 
   Start the script with `python3 word_of_the_day.py`
    This will create a new `token.env` file. Edit this file to specify your discord token.
    E.g. 
    ```bash
    {
        "token": "YOUR_DISCORD_TOKEN_HERE"
    }
    ```
5. **Running the script**:
Start the script again with `python3 word_of_the_day.py`.
As long as the script continues to run it will update your discord status with the Word of the Day each day at a default time of 6:00 AM.

