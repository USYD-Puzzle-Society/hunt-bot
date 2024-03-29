import discord
from discord.ext import commands
from src.config import config
import os
import sentry_sdk

EXEC_ID = config["EXEC_ID"]
COGS_DIR = "cogs"

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", help_command=None, intents=intents)


async def load_cogs():
    for filename in os.listdir("cogs/"):
        if filename.endswith(".py"):
            await bot.load_extension(f"{COGS_DIR}.{filename[:-3]}")
            print(f"Loaded {filename}")


@bot.event
async def on_ready():
    sentry_sdk.init(
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )
    await load_cogs()
    await bot.tree.sync()
    print(f"Connected as {bot.user}.")


# load all available cogs on startup
@bot.command()
@commands.has_role(EXEC_ID)
async def startup(ctx: commands.context.Context):
    await load_cogs()
    await ctx.send(f"Loaded all cogs")


# command to load a cog
@bot.command()
@commands.has_role(EXEC_ID)
async def load(ctx: commands.context.Context, extension):
    await bot.load_extension(f"{COGS_DIR}.{extension}")
    await ctx.send(f"Loaded {extension} cog")


# command to unload a cog
@bot.command()
@commands.has_role(EXEC_ID)
async def unload(ctx: commands.context.Context, extension):
    await bot.unload_extension(f"{COGS_DIR}.{extension}")
    await ctx.send(f"Unloaded {extension} cog")


# command to reload a cog
@bot.command()
@commands.has_role(EXEC_ID)
async def reload(ctx: commands.context.Context, extension):
    await bot.reload_extension(f"{COGS_DIR}.{extension}")
    await ctx.send(f"Reloaded {extension} cog")


@bot.command()
async def sync(ctx: commands.context.Context):
    try:
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)


@bot.command()
async def clear(ctx: commands.context.Context):
    bot.tree.clear_commands(guild=ctx.guild)

    try:
        await bot.tree.sync()
        await ctx.send("Commands cleared.")
    except Exception as e:
        print(e)


bot.run(config["DISCORD_TOKEN"])
