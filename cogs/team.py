import discord
from discord.ext import commands
from discord import app_commands
from discord import Guild

import src.queries.team as team_query
import src.queries.player as player_query


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
    async def leave_team(self, interaction: discord.Interaction):
        # remove team role from user
        user = interaction.user
        guild = interaction.guild

        # get the team name from the user
        discord_id = user.id
        player = await player_query.get_player(discord_id)
        team_name = player.team_name

        team = await team_query.get_team(team_name)
        team_role_id = int(team.team_role_id)
        role = guild.get_role(team_role_id)

        await user.remove_roles(role)

        # delete player
        await player_query.remove_player(discord_id)

        # check amount of people still in team
        # if none, delete team and respective channels
        # also delete the role
        team_members = await team_query.get_team_members(team_name)
        if team_members:
            return

        # if here, then there are no members remaining in the teams
        text_channel = guild.get_channel(team.text_channel_id)
        voice_channel = guild.get_channel(team.voice_channel_id)
        category_channel = guild.get_channel(team.category_channel_id)

        text_channel.delete()
        voice_channel.delete()
        category_channel.delete()
        role.delete()

        # also delete the team


async def setup(bot: commands.Bot):
    await bot.add_cog(Team(bot))
