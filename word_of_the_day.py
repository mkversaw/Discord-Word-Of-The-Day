import discord
import json
import os
import csv
from datetime import datetime
from datetime import timedelta
import schedule
import time
import pytz
import random

# Path to the .env file and word CSV file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
ENV_FILE = os.path.join(BASE_DIR, "token.env")
WORD_FILE = os.path.join(BASE_DIR, "word_list.csv")

failureCount = 0 # times in a row that status update has failed.

def load_time_and_timezone():
    """
    Load the time and time zone from a JSON configuration file.
    """
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
        
        time_str = config.get("time")
        timezone = config.get("timezone")
        
        if not time_str or not timezone:
            raise ValueError("Both 'time' and 'timezone' must be specified in the config file.")
        
        return time_str, timezone
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"Error loading configuration: {e}")
        exit(1)

# parses the users Discord auth token from the env file
def load_token():
    if not os.path.exists(ENV_FILE):
        print("token.env file not found. Creating a new one.")
        with open(ENV_FILE, "w") as f:
            json.dump({"token": ""}, f, indent=4)
        print(f"Please enter your Discord token in {ENV_FILE} and rerun the script.")
        exit(2)

    with open(ENV_FILE, "r") as f:
        data = json.load(f)
        token = data.get("token")
        if not token:
            print("token string missing from token.env.")
            print(f"Please enter your Discord token in {ENV_FILE} and rerun the script.")
            exit(3)
        return token

# Retrieve WOTD from csv
def get_word_of_the_day():
    if not os.path.exists(WORD_FILE):
        print(f"Word file '{WORD_FILE}' not found.")
        exit(4)

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
        exit(5)

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

    try:
        client = SelfClient(word_of_the_day)
        client.run(token)
        # update completed successfully!
        print("status updated to: " + word_of_the_day)
        reschedule_update(update_status)
    except discord.LoginFailure as e:
        print(f"Login failure: {e}")
        print("Verify that discord token is correctly entered. Exiting application")
        exit(1) # unrecoverable
    except discord.HTTPException as e:
        print(f"Discord HTTP error: {e}")
        print("retrying in 5 minutes")
        reschedule_update_after_failure(update_status)
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("retrying in 5 minutes")
        reschedule_update_after_failure(update_status)

def reschedule_update_after_failure(task_func):
    global failureCount
    failureCount += 1
    if failureCount == 3:
        print("Failed to update status after 3 attempts. Exiting application")
        exit(1)
    else:
        schedule.clear()
        schedule.every(5).minutes.do(task_func)



# Schedule at the specified time from the config file,
# with a random delay between 0 and 60 seconds.
def reschedule_update(task_func):
    global failureCount
    failureCount = 0
    time_str, timezone_str = load_time_and_timezone()
    
    # clear any previous tasks
    schedule.clear()

    # Parse time and time zone
    task_time = datetime.strptime(time_str, "%H:%M").time()
    tz = pytz.timezone(timezone_str)
    
    # Get today's datetime for the task in the specified timezone
    now = datetime.now(tz)
    today_task_datetime = tz.localize(datetime.combine(now.date(), task_time))
    
    # If the task time is already past, schedule it for tomorrow
    if today_task_datetime <= now:
        today_task_datetime += timedelta(days=1)
    
    # Add a random delay (0-60 seconds)
    random_delay = random.randint(0, 60)
    scheduled_datetime = today_task_datetime + timedelta(seconds=random_delay)
    
    print(f"Task scheduled to run at {scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    # Schedule the task
    schedule.every().day.at(scheduled_datetime.strftime("%H:%M:%S")).do(task_func)

if __name__ == "__main__":
    # ensure these work before waiting to update the status
    load_time_and_timezone()
    load_token()
    
    # Set status initially. After this the rest will be scheduled.
    update_status()
    while True:
        schedule.run_pending()
        time.sleep(60) # wait one minute
    
