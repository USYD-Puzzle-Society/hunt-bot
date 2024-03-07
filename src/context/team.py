import discord

from typing import List

from src.queries.player import get_player, remove_player
from src.queries.team import get_team, get_team_members, remove_team

from src.models.player import Player


async def get_team_channels(guild: discord.Guild, team_name: str):
    team = await get_team(team_name)

    voice_channel = guild.get_channel(int(team.voice_channel_id))
    text_channel = guild.get_channel(int(team.text_channel_id))
    category_channel = guild.get_channel(int(team.category_channel_id))

    return [voice_channel, text_channel, category_channel]


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


async def remove_role_and_player(
    guild: discord.Guild, player: Player, member: discord.Member
):
    if not player:
        return None

    team = await get_team(player.team_name)
    role = guild.get_role(team.team_role_id)

    await member.remove_roles(role)
    await remove_player(member.id)

    return role


# kicked: a True/False value that lets the function know whether the member
# is leaving the team on their own or is being kicked from the team by
# an admin
async def remove_member_from_team(guild: discord.Guild, member: discord.Member):
    player = await get_player(member.id)

    role = await remove_role_and_player(guild, player, member)

    if not role:
        return None

    team_name = player.team_name

    channels = await get_team_channels(guild, team_name)

    # delete team if no more members
    team_members = await get_team_members(team_name)

    if team_members:
        return "removed"

    # delete roles and channels
    await delete_roles_and_channels([role], channels)

    await remove_team(team_name)

    return "deleted"
