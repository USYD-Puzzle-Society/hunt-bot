import discord
from discord.ext import commands
from discord import app_commands

from src.db.db import main


class Test(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="team")
    async def test_team(self, interaction: discord.Interaction):
        teams = await main()
        await interaction.response.send_message(f"Found: {teams}!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Test(bot))
