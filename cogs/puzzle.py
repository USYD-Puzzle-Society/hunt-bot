from src.config import config

from datetime import datetime
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, view, Button, button

from src.queries.puzzle import get_puzzle, get_completed_puzzles, get_leaderboard
from src.queries.submission import (
    create_submission,
    find_submissions_by_discord_id_and_puzzle_id,
)
from src.queries.player import get_player
from src.queries.team import (
    get_team,
    get_team_members,
    increase_puzzles_solved,
    increase_hints_used,
)

from src.utils.decorators import in_team_channel
from src.context.puzzle import can_access_puzzle, get_accessible_puzzles
from src.context.team import check_if_max_hints, get_next_hint_time


EXEC_ID = config["EXEC_ID"]

HUNT_START_TIME: datetime = config["HUNT_START_TIME"]


class PaginationView(View):
    def __init__(self, pages):
        super().__init__()

        self.page_num = 0
        self.pages = pages

    @button(
        label="<",
        style=discord.ButtonStyle.blurple,
    )
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()

        if self.page_num > 0:
            self.page_num += -1

        await interaction.followup.edit_message(
            message_id=interaction.message.id, embed=self.pages[self.page_num]
        )

    @button(
        label=">",
        style=discord.ButtonStyle.blurple,
    )
    async def next_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()

        if self.page_num < len(self.pages) - 1:
            self.page_num += 1

        await interaction.followup.edit_message(
            message_id=interaction.message.id, embed=self.pages[self.page_num]
        )


class Puzzle(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="submit", description="Submit an answer to a puzzle")
    @in_team_channel
    async def submit_answer(
        self, interaction: discord.Interaction, puzzle_id: str, answer: str
    ):
        await interaction.response.defer()
        answer = answer.lower()

        if datetime.now(tz=ZoneInfo("Australia/Sydney")) < HUNT_START_TIME:
            return await interaction.followup.send(
                "The hunt has not started yet :pensive:"
            )

        puzzle_id = puzzle_id.upper()
        puzzle = await get_puzzle(puzzle_id)
        player = await get_player(interaction.user.id)
        if not puzzle or not await can_access_puzzle(puzzle, player.team_name):
            return await interaction.followup.send(
                "No puzzle with the corresponding ID exists!"
            )
        submissions = await find_submissions_by_discord_id_and_puzzle_id(
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

        await increase_puzzles_solved(player.team_name)

        # check if they have solved all the metas
        if puzzle_id == "UTS-M":
            await interaction.followup.send(
                "The submitted answer is... CORRECT! You've completed all the UTS puzzles and can now see the USYD puzzles."
            )

            # the following is part of an exec's puzzle
            guild = interaction.guild
            team = await get_team(player.team_name)
            team_members = await get_team_members(player.team_name)
            vv_role = guild.get_role(config["VV_ROLE_ID"])

            for member in team_members:
                discord_member = guild.get_member(member.discord_id)
                await discord_member.add_roles(vv_role)

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

            victory_embed = discord.Embed(
                colour=discord.Color.gold(),
                title=f"Team <#{team.text_channel_id}> has finished the hunt!",
                description=f"Congratulate them over in the <#{config['VICTOR_TEXT_CHANNEL_ID']}>",
            )

            await interaction.client.get_channel(config["ADMIN_CHANNEL_ID"]).send(
                embed=victory_embed
            )

            # give team the victor role
            guild = interaction.guild
            team_members = await get_team_members(player.team_name)

            for team_member in team_members:
                discord_member = guild.get_member(team_member.discord_id)
                await discord_member.add_roles(guild.get_role(config["VICTOR_ROLE_ID"]))

            await interaction.followup.send(
                f"Congratulations! You've finished all the puzzles. Feel free to head over to the <#{config['VICTOR_TEXT_CHANNEL_ID']}> in the Victory Lounge."
            )
            return

        completed_puzzles = await get_completed_puzzles(player.team_name)
        # we must have submitted a puzzle correctly at this point
        # if so, we can check if the number of puzzles completed is
        # UTS - 4, USYD - 11 (4 + 1 + 6), or UNSW - 16 (4 + 1 + 6 + 1 + 4) respectively
        num_of_puzzles_completed = len(completed_puzzles)
        if num_of_puzzles_completed == 4:
            await interaction.followup.send(
                "The submitted answer is ...CORRECT! The meta for UTS is now unlocked!"
            )
        elif num_of_puzzles_completed == 11:
            await interaction.followup.send(
                "The submitted answer is ...CORRECT! The meta for USYD is now unlocked!"
            )
        elif num_of_puzzles_completed == 16:
            await interaction.followup.send(
                "The submitted answer is ...CORRECT! The meta for UNSW is now unlocked!"
            )
        else:
            await interaction.followup.send("The submitted answer is ...CORRECT!")

    @app_commands.command(name="list", description="List the available puzzles")
    @in_team_channel
    async def list_puzzles(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if datetime.now(tz=ZoneInfo("Australia/Sydney")) < HUNT_START_TIME:
            return await interaction.followup.send(
                "The hunt has not started yet :pensive:"
            )

        player = await get_player(interaction.user.id)
        puzzles = await get_accessible_puzzles(player.team_name)
        embed = discord.Embed(title="Current Puzzles", color=discord.Color.greyple())

        puzzle_ids = []
        puzzle_name_links = []
        puzzle_answers = []
        for puzzle in puzzles:
            submissions = await find_submissions_by_discord_id_and_puzzle_id(
                player.discord_id, puzzle.puzzle_id
            )

            if any([submission.submission_is_correct for submission in submissions]):
                puzzle_ids.append(f":white_check_mark: {puzzle.puzzle_id}")
                puzzle_answers.append(f"{puzzle.puzzle_answer}")
            else:
                puzzle_ids.append(puzzle.puzzle_id)
                puzzle_answers.append("?")

            puzzle_name_links.append(f"[{puzzle.puzzle_name}]({puzzle.puzzle_link})")

        embed.add_field(name="ID", value="\n".join(puzzle_ids), inline=True)
        embed.add_field(name="Puzzles", value="\n".join(puzzle_name_links), inline=True)
        embed.add_field(name="Answers", value="\n".join(puzzle_answers), inline=True)
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="hint",
        description="Request a hint for the puzzle! Please be detailed about what you're stuck on.",
    )
    @in_team_channel
    async def hint(
        self, interaction: discord.Interaction, puzzle_name: str, hint_msg: str
    ):
        await interaction.response.defer()

        if datetime.now(tz=ZoneInfo("Australia/Sydney")) < config["HUNT_START_TIME"]:
            await interaction.followup.send("The hunt has not started yet :pensive:")
            return

        player = await get_player(interaction.user.id)

        max_hints = await check_if_max_hints(player.team_name)
        if max_hints:
            next_hint_time = get_next_hint_time()
            await interaction.followup.send(
                "You have used up all your available hints! "
                + f"Next hint at {next_hint_time}. A new hint is available every hour."
            )

            return

        await increase_hints_used(player.team_name)

        hint_embed = discord.Embed(
            colour=discord.Color.dark_teal(),
            title=f"Hint Request From {interaction.channel.mention}",
            description=f"**Puzzle Name:** {puzzle_name}",
        )

        if hint_msg:
            hint_embed.add_field(name="Details", value=hint_msg)

        await interaction.client.get_channel(config["ADMIN_CHANNEL_ID"]).send(
            embed=hint_embed
        )

        await interaction.followup.send(
            "Your hint request has been submitted! Hang on tight - a hint giver will be with you shortly."
        )

    @app_commands.command(
        name="leaderboard", description="Displays the current leaderboard for teams."
    )
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()

        leaderboard_values = await get_leaderboard()
        TEAMS_PER_EMBED = 10
        num_vals = len(leaderboard_values)
        if num_vals == 0:
            await interaction.followup.send("There are no teams at this time.")
            return

        # getting the ceiling value. i didn't want to import math
        num_embeds = (
            (num_vals // TEAMS_PER_EMBED) + 1
            if num_vals % TEAMS_PER_EMBED != 0
            else num_vals // TEAMS_PER_EMBED
        )

        # each embed will display ten teams
        leaderboard_embeds = [
            discord.Embed(
                title="Leaderboard",
                description="Teams are sorted by the number of puzzles solved."
                + "Ties are broken by the latest correct submission time for each tied team.",
                color=discord.Color.random(),
            )
            for _ in range(num_embeds)
        ]
        leaderboard_text = [("", "", "") for _ in range(num_embeds)]
        for i, val in enumerate(leaderboard_values):
            team_name, puzzles_solved, submission_time = val
            print(leaderboard_text[i // TEAMS_PER_EMBED])
            team_str, puzzles_solved_str, submission_time_str = leaderboard_text[
                i // TEAMS_PER_EMBED
            ]
            team_str += f"{i+1}. {team_name}\n"
            puzzles_solved_str += f"{puzzles_solved}\n"
            submission_time_str += f"{submission_time.strftime('%d/%m %X') if submission_time else 'N/A'}\n"

            leaderboard_text[i // TEAMS_PER_EMBED] = (
                team_str,
                puzzles_solved_str,
                submission_time_str,
            )

        for page_num, embed in enumerate(leaderboard_embeds):
            embed.add_field(name="Team", value=leaderboard_text[page_num][0])
            embed.add_field(name="Puzzles Solved", value=leaderboard_text[page_num][1])
            embed.add_field(
                name="Last Submission Time", value=leaderboard_text[page_num][2]
            )

        await interaction.followup.send(
            embed=leaderboard_embeds[0], view=PaginationView(leaderboard_embeds)
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Puzzle(bot))
