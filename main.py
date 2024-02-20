import discord
from discord.ext import commands
import os

TOKEN = ""
EXEC_ID = "Executives"
COGS_DIR = "cogs"

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)

@bot.event
async def on_ready():
    print(f"Connected as {bot.user}.")

# load all available cogs on startup
@bot.command()
@commands.has_role(EXEC_ID)
async def startup(ctx: commands.context.Context):
    for filename in os.listdir("cogs/"):
        if filename.endswith(".py"):
            await bot.load_extension(f"{COGS_DIR}.{filename[:-3]}")
            print(f"Loaded {filename}")
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
        synced = await bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

with open(".token", 'r') as t:
    TOKEN = t.readline().strip()

bot.run(TOKEN)