import discord
from discord.ext import commands
from discord import app_commands
from discord import Guild


class Team(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="create")
    async def create_team(self, interaction: discord.Interaction, team_name: str):
        # check that user is not already in a team
        user = interaction.user
        guild = interaction.guild

        # include code to check that the name is not already taken
        # will involve a call to the respective sql function

        # if name not taken, add check for profanity and such

        team_role = await Guild.create_role(guild, name=team_name)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            team_role: discord.PermissionOverwrite(read_messages=True),
        }
        category = await Guild.create_category(guild, team_name, overwrites=overwrites)
        await category.create_text_channel(name=team_name)
        await category.create_voice_channel(name=team_name)

        # give role to user
        await user.add_roles(team_role)
        await interaction.response.send_message(
            f'Team "{team_name}" created successfully!'
        )

    @app_commands.command(name="leave")
    async def leave_team(self, interaction: discord.Interaction, team_name: str):
        # remove team role from user
        # if there are no more people in the team, delete the role and channels

        pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Team(bot))
