import os
from dotenv import load_dotenv

load_dotenv()

config: dict[str, str] = {
    "DISCORD_TOKEN": os.environ["DISCORD_TOKEN"],
    "DATABASE_URL": os.environ["DATABASE_URL"],
}
