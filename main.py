import discord
from discord.ext import commands
from src.config import config

TOKEN = ""

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", help_command=None, intents=intents)


@bot.event
async def on_ready():
    print(f"Connected as {bot.user}.")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)


@bot.command()
async def sync(ctx: commands.context.Context):
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)


bot.run(config["DISCORD_TOKEN"])
