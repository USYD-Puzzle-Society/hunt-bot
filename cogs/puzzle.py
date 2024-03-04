from src.config import config

from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands
from discord import app_commands

from src.queries.puzzle import get_puzzle, create_puzzle
from src.queries.submission import (
    create_submission,
    find_submissions_by_player_id_and_puzzle_id,
)
from src.queries.player import get_player
from src.utils.decorators import in_team_channel
from src.context.puzzle import can_access_puzzle, get_accessible_puzzles

EXEC_ID = "Executives"


class Puzzle(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="submit", description="Submit an answer to a puzzle")
    @in_team_channel
    async def submit_answer(
        self, interaction: discord.Interaction, puzzle_id: str, answer: str
    ):
        await interaction.response.defer()
        puzzle = await get_puzzle(puzzle_id)
        player = await get_player(str(interaction.user.id))
        if not puzzle or not await can_access_puzzle(puzzle, player.team_name):
            return await interaction.followup.send(
                "No puzzle with the corresponding ID exists!"
            )
        submissions = await find_submissions_by_player_id_and_puzzle_id(
            player.discord_id, puzzle_id
        )

        if any([submission.submission_is_correct for submission in submissions]):
            return await interaction.followup.send(
                "You have already completed this puzzle!"
            )

        submission_is_correct = puzzle.puzzle_answer == answer

        await create_submission(
            puzzle_id,
            player.team_name,
            datetime.now(tz=ZoneInfo("Australia/Sydney")),
            answer,
            submission_is_correct,
        )

        if not submission_is_correct:
            return await interaction.followup.send("The submitted answer is incorrect!")

        await interaction.followup.send("The submitted answer is ...CORRECT!")

    @app_commands.command(name="list", description="List the available puzzles")
    @in_team_channel
    async def list_puzzles(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player = await get_player(str(interaction.user.id))
        puzzles = await get_accessible_puzzles(player.team_name)
        embed = discord.Embed(title="Current Puzzles", color=discord.Color.greyple())

        puzzle_ids, puzzle_links = zip(
            *[
                (puzzle.puzzle_id, f"[{puzzle.puzzle_name}]({puzzle.puzzle_link})")
                for puzzle in puzzles
            ]
        )

        embed.add_field(name="ID", value="\n".join(puzzle_ids), inline=True)
        embed.add_field(name="Puzzles", value="\n".join(puzzle_links), inline=True)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="hint", description="Request a hint for the puzzle!")
    @in_team_channel
    async def hint(self, interaction: discord.Interaction):
        await interaction.response.defer()
        team = await get_player(str(interaction.user.id))
        await interaction.client.get_channel(config["ADMIN_CHANNEL_ID"]).send(
            f"Hint request submitted from team {team.team_name}! {interaction.channel.mention}"
        )
        await interaction.followup.send(
            "Your hint request has been submitted! Hang on tight - a hint giver will be with you shortly."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Puzzle(bot))
