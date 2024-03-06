import discord

from typing import List

from src.queries.player import get_player, remove_player
from src.queries.team import get_team, get_team_members, remove_team


async def get_team_role_and_channels(guild: discord.Guild, team_name: str):
    team = await get_team(team_name)
    role = guild.get_role(int(team.team_role_id))

    voice_channel = await guild.get_channel(int(team.voice_channel_id))
    text_channel = await guild.get_channel(int(team.text_channel_id))
    category_channel = await guild.get_channel(int(team.category_channel_id))

    return role, [voice_channel, text_channel, category_channel]


async def delete_roles_and_channels(
    roles: List[discord.Role],
    channels: List[
        discord.TextChannel | discord.VoiceChannel | discord.CategoryChannel
    ],
):
    for role in roles:
        await role.delete()

    for channel in channels:
        await channel.delete()


# kicked: a True/False value that lets the function know whether the member
# is leaving the team on their own or is being kicked from the team by
# an admin
async def remove_member_from_team(
    interaction: discord.Interaction, member: discord.Member, kicked: bool
):
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild

    # get player object from member
    player = await get_player(member.id)

    if not player:
        if kicked:
            await interaction.followup.send(
                f"{member.display_name} is not part of a team.", ephemeral=True
            )
            return
        else:
            await interaction.followup.send(
                "You are not part of a team.", ephemeral=True
            )
            return

    team_name = player.team_name

    role, channels = await get_team_role_and_channels(guild, team_name)

    # remove their team role
    await member.remove_roles(role)

    # delete player
    await remove_player(member.id)

    # delete team if no more members
    team_members = await get_team_members(team_name)

    if team_members:
        if kicked:
            await interaction.followup.send(
                f"{member.display_name} has been successfully kicked from {team_name}.",
                ephemeral=True,
            )
            return
        else:
            await interaction.followup.send("You have left the team.", ephemeral=True)
            return

    # delete roles and channels
    await delete_roles_and_channels([role], channels)

    await remove_team(team_name)

    if kicked:
        await interaction.followup.send(
            f"{member.display_name} has been successfully kicked from {team_name}. "
            + "Since the team is empty, the corresponding roles and channels will be deleted.",
            ephemeral=True,
        )
        return
    else:
        await interaction.followup.send(
            "You have left the team. Since there are no members left in the team, the channels will be deleted.",
            ephemeral=True,
        )
