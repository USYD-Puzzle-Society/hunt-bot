import os
from dotenv import load_dotenv

load_dotenv(override=True)

config: dict[str, str] = {
    "DISCORD_TOKEN": os.environ["DISCORD_TOKEN"],
    "DATABASE_URL": os.environ["DATABASE_URL"],
    "ADMIN_CHANNEL_ID": int(os.environ["ADMIN_CHANNEL_ID"]),
}
