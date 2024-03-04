import os

import discord
from discord.ext import commands
from discord import app_commands

from typing import Literal

from src.queries.puzzle import (
    get_puzzle,
    get_puzzles_by_uni,
    create_puzzle,
    delete_puzzle,
)

from src.config import config

EXEC_ID = "Executives"


class Admin(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_id(self, num: int, uni: str):
        if num > 9:
            return f"{uni}-{num}"
        else:
            return f"{uni}-0{num}"

    @app_commands.command(name="create_puzzle", description="Create a new puzzle")
    @commands.has_role(EXEC_ID)
    async def create_puzzle(
        self,
        interaction: discord.Interaction,
        puzzle_name: str,
        puzzle_answer: str,
        puzzle_link: str,
        uni: Literal["UTS", "UNSW", "USYD", "METAMETA"],
        meta: bool = False,
        puzzle_author: str = "",
    ):
        await interaction.response.defer()

        """
        puzzle_id will be made to fit the form
        [UNI]-[ID_NUM]
        e.g USYD-09
        UTS-02
        UNSW-03

        except for the meta which will be
        [UNI]-M
        e.g USYD-M
        """

        """
        Get all puzzles from the given uni (puzzles are given in ascending order)
        start at 1 and count up through each puzzle. if the number matches the
        puzzle id, then that id number is not missing and we keep going.
        if we finish going through all the puzzles with none missing then
        id_num will be equal to the next number in the sequence.
        if we see a puzzle whose id doesn't match the current id_num, then
        that means a puzzle with that id was removed and we now fill that hole.
        """

        puzzle_id = ""
        # if the puzzle is the meta, then skip these steps
        if meta:
            puzzle_id = f"{uni}-M"

            # check if meta already exists
            meta_puzz = await get_puzzle(puzzle_id)
            if meta_puzz:
                await interaction.followup.send(
                    f"Meta puzzle for {uni} already exists!"
                )
                return
        else:
            uni_puzzles = await get_puzzles_by_uni(uni)
            id_num = 1
            for puzz in uni_puzzles:
                if puzz.puzzle_id == self.get_id(id_num, uni):
                    id_num += 1
                else:
                    break

            puzzle_id = self.get_id(id_num, uni)

        # puzzle_exists = await get_puzzle(puzzle_id)
        # if puzzle_exists:
        #     await interaction.followup.send(f"Puzzle {puzzle_id} already exists!")
        #     return

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
