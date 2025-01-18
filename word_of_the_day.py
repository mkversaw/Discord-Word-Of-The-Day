import discord
import json
import os
import csv
from datetime import datetime
import schedule
import time

# Path to the .env file and word CSV file
ENV_FILE = "token.env"
WORD_FILE = "word_list.csv"

# parses the users Discord auth token from the env file
def load_token():
    if not os.path.exists(ENV_FILE):
        print("token.env file not found. Creating a new one.")
        with open(ENV_FILE, "w") as f:
            json.dump({"token": ""}, f, indent=4)
        print(f"Please enter your Discord token in {ENV_FILE} and rerun the script.")
        exit()

    with open(ENV_FILE, "r") as f:
        data = json.load(f)
        token = data.get("token")
        if not token:
            print("token string missing from token.env.")
            print(f"Please enter your Discord token in {ENV_FILE} and rerun the script.")
            exit()
        return token

# Retrieve WOTD from csv
def get_word_of_the_day():
    if not os.path.exists(WORD_FILE):
        print(f"Word file '{WORD_FILE}' not found.")
        exit()

    with open(WORD_FILE, "r") as f:
        reader = csv.reader(f)
        words = list(reader)

    header = words[0]
    
    year = datetime.now().year
    year_index = year - 2025

    if year_index < 0 or year_index >= len(header):
        print(f"Year {year} is out of range in the word file.")
        exit()

    day_of_year = datetime.now().timetuple().tm_yday - 1  # Day of the year (0-364, or 0-365 on leap years)
    if day_of_year + 1 >= len(words):
        print("Not enough words in the file for the current day.")
        exit()

    return words[day_of_year + 1][year_index]  # Return the word for the day

class SelfClient(discord.Client):
    def __init__(self, word_of_the_day):
        super().__init__(activity = discord.CustomActivity(
            name=word_of_the_day
        ))

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        await self.close()

def update_status():
    token = load_token()
    word_of_the_day = "WOTD: " + get_word_of_the_day()
    
    client = SelfClient(word_of_the_day)
    client.run(token)

schedule.every().day.at("06:00").do(update_status)

if __name__ == "__main__":
    update_status()
    while True:
        schedule.run_pending()
        time.sleep(60) # wait one minute
    
