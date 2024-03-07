import discord
from discord.ext import commands
from discord import app_commands

import src.queries.team as team_query
import src.queries.player as player_query

from src.context.team import remove_member_from_team

BOT_ID = 1208986388226121849
MAX_TEAM_SIZE = 6
EXEC_ID = "Executives"


class Team(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="create", description="Create a new team.")
    async def create_team(self, interaction: discord.Interaction, team_name: str):
        # check that user is not already in a team
        user = interaction.user
        guild = interaction.guild

        await interaction.response.defer(ephemeral=True)

        if await player_query.get_player(user.id):
            await interaction.followup.send(
                "You are already in a team. Please leave the team before creating a new one.",
                ephemeral=True,
            )
            return

        # check team name is not already taken
        if await team_query.get_team(team_name):
            await interaction.followup.send(
                f'Team "{team_name}" is already taken. Please choose a different team name.',
                ephemeral=True,
            )
            return

        # additionally check that the name is not the same as the exec role
        if team_name.lower() == EXEC_ID.lower():
            await interaction.followup.send(
                f'You cannot name yourself "{team_name}". Please choose a different team name.'
            )
            return

        # if name not taken, add check for profanity and such
        team_role = await guild.create_role(name=team_name)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            team_role: discord.PermissionOverwrite(read_messages=True),
            # this line allows the bot to see the private channels it creates
            guild.get_member(self.bot.application_id): discord.PermissionOverwrite(
                read_messages=True
            ),
        }
        category = await guild.create_category(team_name, overwrites=overwrites)
        text_channel = await category.create_text_channel(name=team_name)
        voice_channel = await category.create_voice_channel(name=team_name)

        # create team in database
        await team_query.create_team(
            team_name,
            category.id,
            voice_channel.id,
            text_channel.id,
            team_role.id,
        )

        # add player to database
        await player_query.add_player(user.id, team_name)

        # give role to user
        await user.add_roles(team_role)

        await interaction.followup.send(
            content=f'Team "{team_name}" created successfully!', ephemeral=True
        )

    @app_commands.command(name="leave", description="Leave your current team.")
    async def leave_team(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user = interaction.user

        status = await remove_member_from_team(interaction.guild, user)

        if status is None:
            await interaction.followup.send(
                "You are not part of a team.", ephemeral=True
            )
            return

        elif status == "removed":
            await interaction.followup.send("You have left the team.", ephemeral=True)
            return

        elif status == "deleted":
            await interaction.followup.send(
                "You have left the team. Since there are no members left, the channels will be deleted.",
                ephemeral=True,
            )
            return

    @app_commands.command(
        name="invite", description="Invite another member into your team!"
    )
    async def invite(
        self, interaction: discord.Interaction, invited_user: discord.Member
    ):
        user = interaction.user
        guild = interaction.guild

        await interaction.response.defer(ephemeral=True)

        # check user is already in a team
        player = await player_query.get_player(user.id)
        if not player:
            await interaction.followup.send(
                "You must be in a team to use this command.", ephemeral=True
            )
            return

        team_name = player.team_name

        # check invited user is not already in a team
        if await player_query.get_player(invited_user.id):
            await interaction.followup.send(
                "The user you're trying to invite is already in a team.", ephemeral=True
            )
            return

        # check that team is not full
        if len(await team_query.get_team_members(team_name)) == MAX_TEAM_SIZE:
            await interaction.followup.send("Your team is full.", ephemeral=True)
            return

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

        """
        Completely optional but we could make it so players can add
        custom accept/reject messages.
        """

        # add invited user to the team and database
        async def accept_callback(interaction: discord.Interaction):
            new_player = interaction.user
            team = await team_query.get_team(team_name)

            await interaction.response.defer()

            # check team still exists
            if not team:
                cancel_embed = discord.Embed(
                    colour=discord.Color.orange(),
                    title=f"{team_name} Does Not Exist",
                    description=f"Sorry, looks like that team has been deleted :(",
                )
                await interaction.followup.edit_message(
                    message_id=interaction.message.id, embed=cancel_embed, view=None
                )
                return

            # check team is not full
            team_members = await team_query.get_team_members(team_name)
            if team_members == MAX_TEAM_SIZE:
                full_embed = discord.Embed(
                    colour=discord.Color.blue(),
                    title=f"{team_name} Is Full",
                    description=f"You can no longer join the team :(",
                )
                await interaction.followup.edit_message(
                    message_id=interaction.message.id, embed=full_embed, view=None
                )
                return

            # add new user to team
            await invited_user.add_roles(guild.get_role(int(team.team_role_id)))
            await player_query.add_player(new_player.id, team_name)

            # edit message so that user can't click again
            accept_embed = discord.Embed(
                colour=discord.Color.green(),
                title=f"{team_name} Invitation Accepted",
                description=f"You are now part of {team_name}! Join your teammates at <#{team.text_channel_id}>.",
            )

            await interaction.followup.edit_message(
                message_id=interaction.message.id, embed=accept_embed, view=None
            )

        async def reject_callback(interaction: discord.Interaction):
            await interaction.response.defer()

            reject_embed = discord.Embed(
                color=discord.Color.red(),
                title=f"{team_name} Invitation Rejected",
            )
            await interaction.followup.edit_message(
                message_id=interaction.message.id, embed=reject_embed, view=None
            )

        accept_btn.callback = accept_callback
        reject_btn.callback = reject_callback

        await invited_user.send(embed=embed, view=view)
        await interaction.followup.send(
            f"{invited_user} has been invited to your team.", ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Team(bot))
