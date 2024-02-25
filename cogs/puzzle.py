from datetime import datetime
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands
from discord import app_commands

from src.queries.puzzle import find_puzzle
from src.queries.submission import create_submission
from src.utils.decorators import in_team_channel


class Puzzle(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="submit", description="Submit an answer to a puzzle")
    @in_team_channel
    async def submit_answer(
        self, interaction: discord.Interaction, puzzle_id: str, answer: str
    ):
        puzzle = await find_puzzle(puzzle_id)
        if not puzzle:
            return await interaction.response.send_message(
                "No puzzle with the corresponding id exist!"
            )
        # TODO: retrieve team name
        team_name = "any"

        if puzzle.puzzle_answer != answer:
            await create_submission(
                puzzle_id,
                team_name,
                datetime.now(tz=ZoneInfo("Australia/Sydney")),
                answer,
                False,
            )
            return await interaction.response.send_message(
                "The submitted answer is incorrect!"
            )

        await create_submission(
            puzzle_id,
            team_name,
            datetime.now(tz=ZoneInfo("Australia/Sydney")),
            answer,
            True,
        )
        return await interaction.response.send_message(
            "The submitted answer is correct!"
        )

    @app_commands.command(name="list", description="List the available puzzles")
    @in_team_channel
    async def list_puzzles(self, interaction: discord.Interaction):
        # first, queries in the submission table to find how many meta the team has solved

        # from this information, calculate the puzzles the solver have access to

        pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Puzzle(bot))
