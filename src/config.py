from datetime import datetime
import os
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv(override=True)

config: dict[str, str | int | datetime] = {
    "DISCORD_TOKEN": os.environ["DISCORD_TOKEN"],
    "DATABASE_URL": os.environ["DATABASE_URL"],
    "ADMIN_CHANNEL_ID": int(os.environ["ADMIN_CHANNEL_ID"]),
    "VICTOR_ROLE_ID": int(os.environ["VICTOR_ROLE_ID"]),
    "VICTOR_TEXT_CHANNEL_ID": int(os.environ["VICTOR_TEXT_CHANNEL_ID"]),
    "EXEC_ID": "Executives",
    "HUNT_START_TIME": datetime(
        2024, 3, 16, 9, 15, tzinfo=ZoneInfo("Australia/Sydney")
    ),
}
