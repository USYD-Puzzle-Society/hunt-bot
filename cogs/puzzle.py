from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands
from discord import app_commands

from src.queries.puzzle import get_puzzle, create_puzzle
from src.queries.submission import create_submission
from src.queries.player import get_player
from src.utils.decorators import in_team_channel
from src.context.puzzle import can_access_puzzle, get_accessible_puzzles


class Puzzle(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="submit", description="Submit an answer to a puzzle")
    @in_team_channel
    async def submit_answer(
        self, interaction: discord.Interaction, puzzle_id: str, answer: str
    ):
        puzzle = await get_puzzle(puzzle_id)
        if not puzzle or not await can_access_puzzle(puzzle, interaction.user.id):
            return await interaction.response.send_message(
                "No puzzle with the corresponding id exist!"
            )
        player = await get_player(str(interaction.user.id))

        submission_is_correct = puzzle.puzzle_answer == answer

        await create_submission(
            puzzle_id,
            player.team_name,
            datetime.now(tz=ZoneInfo("Australia/Sydney")),
            answer,
            submission_is_correct,
        )

        if not submission_is_correct:
            return await interaction.response.send_message(
                "The submitted answer is incorrect!"
            )

        await interaction.response.send_message("The submitted answer is ...CORRECT!")

    @app_commands.command(name="list", description="List the available puzzles")
    @in_team_channel
    async def list_puzzles(self, interaction: discord.Interaction):
        puzzles = await get_accessible_puzzles(interaction.user.id)
        embed = discord.Embed(title="Current Puzzles", color=discord.Color.greyple())

        puzzle_ids, puzzle_links = zip(
            *[
                (puzzle.puzzle_id, f"[{puzzle.puzzle_name}]({puzzle.puzzle_link})")
                for puzzle in puzzles
            ]
        )

        embed.add_field(name="ID", value="\n".join(puzzle_ids), inline=True)
        embed.add_field(name="Puzzles", value="\n".join(puzzle_links), inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="create", description="Create a puzzle (must have admin role)."
    )
    async def create_puzzles(
        self,
        interaction: discord.Interaction,
        puzzle_id: str,
        puzzle_name: str,
        puzzle_answer: str,
        puzzle_author: str,
        puzzle_link: str,
        uni: Literal["UTS", "UNSW", "USYD", "METAMETA"],
    ):
        if "Executives" not in [role.name for role in interaction.user.roles]:
            return await interaction.response.send_message(
                f"You don't have permission to do this!"
            )

        await create_puzzle(
            puzzle_id, puzzle_name, puzzle_answer, puzzle_author, puzzle_link, uni
        )

        await interaction.response.send_message(f"Puzzle {puzzle_name} created!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Puzzle(bot))
