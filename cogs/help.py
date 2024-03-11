import discord
from discord import app_commands
from discord.ext import commands

from src.config import config

EXEC_ID = config["EXEC_ID"]


class Help(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="commands", description="Get a list of bot commands")
    async def help_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user = interaction.user
        user_roles = [role.name for role in user.roles]

        admin_commands = [
            "`/admin create_puzzle [PUZZLE_NAME] [PUZZLE_ANSWER] [PUZZLE_LINK] [UNI] [META] [PUZZLE_AUTHOR]` - Creates a new puzzle with given arguments.",
            "`/admin delete_puzzle [PUZZLE_ID]` - Deletes the puzzle with the given ID.",
            "`/admin list_puzzles` - Lists all created puzzles along with their answers"
            "`/admin set_hint_channel` - Sets the current channel to be the new channel for receiving hint requests.",
        ]

        team_commands = [
            "`/team create [TEAM_NAME]` - Create a new team with the given name.",
            "`/team leave` - Leave your current team. Deletes the team if no more members.",
            "`/team invite [INVITED_USER]` - Invites the given user into your team. They can accept or reject.",
        ]

        puzzle_commands = [
            "`/puzzle submit [PUZZLE_ID] [ANSWER]` - Submits and checks your answer for the specified puzzle.",
            "`/puzzle list` - Lists all the puzzles available.",
            "`/puzzle hint` - Sends a hint request to the execs.",
        ]

        help_embed = discord.Embed(description="List of Commands")

        if EXEC_ID in user_roles:
            help_embed.colour = discord.Color.green()
            help_embed.add_field(name="Admin", value="\n".join(admin_commands))

        help_embed.add_field(name="Team", value="\n".join(team_commands))
        help_embed.add_field(name="Puzzle", value="\n".join(puzzle_commands))

        await interaction.followup.send(embed=help_embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
