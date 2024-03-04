import os
from dotenv import load_dotenv

load_dotenv(override=True)

config: dict[str, str] = {
    "DISCORD_TOKEN": os.environ["DISCORD_TOKEN"],
    "DATABASE_URL": os.environ["DATABASE_URL"],
    "ADMIN_CHANNEL_ID": int(os.environ["ADMIN_CHANNEL_ID"]),
    "VICTOR_ROLE_ID": int(os.environ["VICTOR_ROLE_ID"]),
    "VICTOR_TEXT_CHANNEL_ID": int(os.environ["VICTOR_TEXT_CHANNEL_ID"]),
}
