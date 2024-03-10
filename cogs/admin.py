import os

import discord
from discord.ext import commands
from discord import app_commands

from discord.app_commands.errors import CommandInvokeError

from typing import Literal

from src.queries.puzzle import (
    get_puzzle,
    get_all_puzzles,
    get_puzzles_by_uni,
    create_puzzle,
    delete_puzzle,
)
from src.queries.player import get_player, remove_player, add_player
from src.queries.team import get_team, get_team_members, remove_team

from src.config import config

from src.context.team import remove_member_from_team

EXEC_ID = "Executives"
MAX_TEAM_SIZE = 6


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

        AND except for the metameta which will just be
        METAMETA
        
        Get all puzzles from the given uni (puzzles are given in ascending order)
        start at 1 and count up through each puzzle. if the number matches the
        puzzle id, then that id number is not missing and we keep going.
        if we finish going through all the puzzles with none missing then
        id_num will be equal to the next number in the sequence.
        if we see a puzzle whose id doesn't match the current id_num, then
        that means a puzzle with that id was removed and we now fill that hole.
        """

        # check for metameta
        puzzle_id = ""
        if uni == "METAMETA":
            puzzle_id = uni
            metameta = await get_puzzle(uni)

            if metameta:
                await interaction.followup.send(f"{uni} already exists!")
                return

        # if the puzzle is the meta, then skip these steps
        elif meta:
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

        await create_puzzle(
            puzzle_id, puzzle_name, puzzle_answer, puzzle_author, puzzle_link, uni
        )

        await interaction.followup.send(
            f"Puzzle {puzzle_name} created! The ID for this puzzle is {puzzle_id}"
        )

    @app_commands.command(
        name="delete_puzzle", description="Delete an existing puzzle."
    )
    @commands.has_role(EXEC_ID)
    async def delete_puzzle(self, interaction: discord.Interaction, puzzle_id: str):
        await interaction.response.defer()

        deleted = await delete_puzzle(puzzle_id.upper())

        if not deleted:
            await interaction.followup.send(
                f"Puzzle {puzzle_id.upper()} does not exist."
            )
            return

        await interaction.followup.send(f"Puzzle {puzzle_id.upper()} deleted.")

    @app_commands.command(name="list_puzzles", description="List all created puzzles.")
    @commands.has_role(EXEC_ID)
    async def list_puzzles(self, interaction: discord.Interaction):
        await interaction.response.defer()

        all_puzzles = await get_all_puzzles()

        all_puzzle_ids = []
        all_puzzle_name_links = []
        all_puzzle_answers = []
        for puzzle in all_puzzles:
            all_puzzle_ids.append(puzzle.puzzle_id)
            all_puzzle_name_links.append(
                f"[{puzzle.puzzle_name}]({puzzle.puzzle_link})"
            )
            all_puzzle_answers.append(f"||{puzzle.puzzle_answer}||")

        puzzles_embed = discord.Embed(
            colour=discord.Color.random(),
            title="List of Puzzles",
            description="Puzzles sorted by uni.",
        )

        puzzles_embed.add_field(name="IDs", value="\n".join(all_puzzle_ids))
        puzzles_embed.add_field(name="Puzzles", value="\n".join(all_puzzle_name_links))
        puzzles_embed.add_field(name="Answers", value="\n".join(all_puzzle_answers))

        await interaction.followup.send(embed=puzzles_embed)

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

    @app_commands.command(
        name="remove_member", description="Forcibly removes a member from a team."
    )
    @commands.has_role(EXEC_ID)
    async def remove_member(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        await interaction.response.defer(ephemeral=True)
        status = await remove_member_from_team(interaction.guild, member)

        if status is None:
            await interaction.followup.send(
                f"{member.display_name} is not part of a team.", ephemeral=True
            )
            return

        elif status == "removed":
            await interaction.followup.send(
                f"{member.display_name} has been successfully kicked from the team.",
                ephemeral=True,
            )
            return

        elif status == "deleted":
            try:
                await interaction.followup.send(
                    f"{member.display_name} has been successfully kicked from the team. "
                    + "Since the team is empty, the corresponding roles and channels will be deleted.",
                    ephemeral=True,
                )
            except CommandInvokeError:
                return

            return

    @app_commands.command(
        name="add_member",
        description="Adds someone to a team. Only use this when they are unable to be invited.",
    )
    @commands.has_role(EXEC_ID)
    async def add_member(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        team_name: str,
    ):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild

        player = await get_player(member.id)
        if player:
            await interaction.followup.send(
                f"{member.display_name} is already in a team.", ephemeral=True
            )
            return

        team = await get_team(team_name)
        if not team:
            await interaction.followup.send(
                f"{team_name} does not exist. Did you type the name correctly?",
                ephemeral=True,
            )
            return

        team_members = await get_team_members(team_name)
        if len(team_members) == MAX_TEAM_SIZE:
            await interaction.followup.send(f"{team_name} is full!", ephemeral=True)
            return

        # if all checks pass, add the member to the team
        await add_player(member.id, team_name)

        # give member the team role
        await member.add_roles(guild.get_role(team.team_role_id))

        await interaction.followup.send(
            f"{member.display_name} is now part of the {team_name}!", ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
