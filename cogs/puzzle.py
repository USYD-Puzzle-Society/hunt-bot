from src.config import config

from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands
from discord import app_commands

from src.queries.puzzle import get_puzzle, get_completed_puzzles
from src.queries.submission import (
    create_submission,
    find_submissions_by_player_id_and_puzzle_id,
)
from src.queries.player import get_player
from src.queries.team import get_team, get_team_members

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

        puzzle_id = puzzle_id.upper()
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

        # check if they have solved all the metas
        if puzzle_id == "UTS-M":
            await interaction.followup.send(
                "The submitted answer is... CORRECT! You've completed all the UTS puzzles and can now see the USYD puzzles."
            )
            return

        elif puzzle_id == "USYD-M":
            await interaction.followup.send(
                "The submitted answer is... CORRECT! You've completed all the USYD puzzles and can now see the UNSW puzzles."
            )
            return

        elif puzzle_id == "UNSW-M":
            await interaction.followup.send(
                "The submitted answer is... CORRECT! You've completed all the metas and can now access the METAMETA!"
            )
            return

        elif puzzle_id == "METAMETA":
            team = await get_team(player.team_name)
            await interaction.client.get_channel(config["ADMIN_CHANNEL_ID"]).send(
                f"Team <#{team.text_channel_id}> has finished all the puzzles!"
            )

            # give team the victor role
            guild = interaction.guild
            team_members = await get_team_members(player.team_name)

            for team_member in team_members:
                discord_member = guild.get_member(int(team_member.discord_id))
                await discord_member.add_roles(guild.get_role(config["VICTOR_ROLE_ID"]))

            await interaction.followup.send(
                f"Congratulations! You've finished all the puzzles. Feel free to head over to the <#{config['VICTOR_TEXT_CHANNEL_ID']}> in the Victory Lounge."
            )
            return

        await interaction.followup.send("The submitted answer is ...CORRECT!")

    @app_commands.command(name="list", description="List the available puzzles")
    @in_team_channel
    async def list_puzzles(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player = await get_player(str(interaction.user.id))
        puzzles = await get_accessible_puzzles(player.team_name)
        embed = discord.Embed(title="Current Puzzles", color=discord.Color.greyple())

        puzzle_ids = []
        puzzle_name_links = []
        for puzzle in puzzles:
            submissions = await find_submissions_by_player_id_and_puzzle_id(
                str(player.discord_id), puzzle.puzzle_id
            )

            if any([submission.submission_is_correct for submission in submissions]):
                puzzle_ids.append(f":white_check_mark: {puzzle.puzzle_id}")
            else:
                puzzle_ids.append(puzzle.puzzle_id)

            puzzle_name_links.append(f"[{puzzle.puzzle_name}]({puzzle.puzzle_link})")

        embed.add_field(name="ID", value="\n".join(puzzle_ids), inline=True)
        embed.add_field(name="Puzzles", value="\n".join(puzzle_name_links), inline=True)
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
