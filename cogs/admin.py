import os

import discord
from discord.ext import commands
from discord import app_commands

from typing import Literal

from src.queries.puzzle import get_puzzle, create_puzzle, delete_puzzle

from src.config import config

EXEC_ID = "Executives"


class Admin(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="create_puzzle", description="Create a new puzzle")
    @commands.has_role(EXEC_ID)
    async def create_puzzle(
        self,
        interaction: discord.Interaction,
        puzzle_id: str,
        puzzle_name: str,
        puzzle_answer: str,
        puzzle_author: str,
        puzzle_link: str,
        uni: Literal["UTS", "UNSW", "USYD", "METAMETA"],
    ):
        await interaction.response.defer()

        puzzle_exists = await get_puzzle(puzzle_id)
        if puzzle_exists:
            await interaction.followup.send(f"Puzzle {puzzle_id} already exists!")
            return

        await create_puzzle(
            puzzle_id, puzzle_name, puzzle_answer, puzzle_author, puzzle_link, uni
        )

        await interaction.followup.send(f"Puzzle {puzzle_name} created!")

    @app_commands.command(
        name="delete_puzzle", description="Delete an existing puzzle."
    )
    @commands.has_role(EXEC_ID)
    async def delete_puzzle(self, interaction: discord.Interaction, puzzle_id: str):
        await interaction.response.defer()

        deleted = await delete_puzzle(puzzle_id)

        if not deleted:
            await interaction.followup.send(f"Puzzle {puzzle_id} does not exist.")
            return

        await interaction.followup.send(f"Puzzle {puzzle_id} deleted.")

    @app_commands.command(
        name="set_hint_channel",
        description="Set the current channel to be the hint channel.",
    )
    @commands.has_role(EXEC_ID)
    async def set_hint_channel(self, interaction: discord.Interaction):
        channel = interaction.channel

        await interaction.response.defer()

        # set new channel id in environment variable
        os.environ["ADMIN_CHANNEL_ID"] = str(channel.id)

        # change the config variable
        config["ADMIN_CHANNEL_ID"] = channel.id

        await interaction.followup.send(
            f"Hints will now be redirected to <#{channel.id}>"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))