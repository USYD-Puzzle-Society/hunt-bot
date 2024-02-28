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

        # check team name is not already taken
        if await team_query.get_team(team_name):
            await interaction.response.send_message(
                f'Team "{team_name}" is already taken. Please choose a different team name.'
            )

        # if name not taken, add check for profanity and such
        team_role = await guild.create_role(name=team_name)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            team_role: discord.PermissionOverwrite(read_messages=True),
        }
        category = await guild.create_category(team_name, overwrites=overwrites)
        text_channel = await category.create_text_channel(name=team_name)
        voice_channel = await category.create_voice_channel(name=team_name)

        # create team in database
        await team_query.create_team(
            team_name,
            str(category.id),
            str(voice_channel.id),
            str(text_channel.id),
            str(team_role.id),
        )

        # add player to database
        await player_query.add_player(user.id, team_name)

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
        await team_query.remove_team(team_name)

    @app_commands.command(name="invite")
    async def invite(
        self, interaction: discord.Interaction, invited_user: discord.Member
    ):
        user = interaction.user
        guild = interaction.guild

        # check user is already in a team
        player = await player_query.get_player(user.id)
        if not player:
            interaction.response.send_message(
                "You must be in a team to use this command."
            )

        team_name = player.team_name

        # check invited user is not already in a team
        if await player_query.get_player(invited_user.id):
            interaction.response.send_message(
                "The user you're trying to invite is already in a team."
            )

        # otherwise send an invite
        embed = discord.Embed(
            title=f"{team_name} Invitation",
            description=f"{user.name} has invited you to their team!",
        )

        accept_btn = discord.ui.Button(label="Accept", style=discord.ButtonStyle.green)
        reject_btn = discord.ui.Button(label="Reject", style=discord.ButtonStyle.red)

        view = discord.ui.View()
        view.add_item(accept_btn)
        view.add_item(reject_btn)

        # add invited user to the team and database
        async def accept_callback(interaction: discord.Interaction):
            team = await team_query.get_team(team_name)
            invited_user.add_roles(guild.get_role(int(team.team_role_id)))

            # test line. delete later
            print(interaction.user())

        async def reject_callback(interaction: discord.Interaction):
            await user.send(content="Your team invitation has been declined.")

        accept_btn.callback = accept_callback
        reject_btn.callback = reject_callback

        await invited_user.send(embed=embed, view=view)
        await interaction.response.send_message(
            f"{invited_user} has been invited to your team.", ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Team(bot))
