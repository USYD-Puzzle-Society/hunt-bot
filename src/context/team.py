import discord

from typing import List

from src.queries.player import get_player, remove_player
from src.queries.puzzle import get_finished_teams
from src.queries.team import get_team, get_team_members, remove_team

from src.models.player import Player

from src.config import config

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

SECONDS_BETWEEN_HINTS = 7200  # how many seconds between each new hint
SECONDS_IN_AN_HOUR = 3600
HOURS_IN_A_DAY = 24


async def get_team_channels(guild: discord.Guild, team_name: str):
    team = await get_team(team_name)

    voice_channel = guild.get_channel(team.voice_channel_id)
    text_channel = guild.get_channel(team.text_channel_id)
    category_channel = guild.get_channel(team.category_channel_id)

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


async def remove_member_from_team(guild: discord.Guild, member: discord.Member):
    player = await get_player(member.id)

    role = await remove_role_and_player(guild, player, member)

    if not role:
        return None

    team_name = player.team_name

    # delete team if no more members
    team_members = await get_team_members(team_name)

    if team_members:
        return "removed"

    channels = await get_team_channels(guild, team_name)

    # delete roles and channels
    await delete_roles_and_channels([role], channels)

    await remove_team(team_name)

    return "deleted"


def get_max_hints():
    now = datetime.now(tz=ZoneInfo("Australia/Sydney")) + timedelta(hours=1)
    start: datetime = config["HUNT_START_TIME"]

    if now < start:
        return 0

    time_difference = now - start
    max_hints = int(time_difference.total_seconds()) // SECONDS_BETWEEN_HINTS

    return max_hints


async def check_if_max_hints(team_name: str):
    team = await get_team(team_name)

    # check if top 3 has been taken
    # unlimited hints if so and we just return False
    finished_teams = await get_finished_teams()
    if len(finished_teams) >= 3:
        return False

    # check how many hints would be available
    # if no hints were used
    # hints are given out 1 per hour
    # so total number of hints that would be available
    # is the same as the number of hours that have passed
    total_hints = get_max_hints()
    if team.hints_used < total_hints:
        return False

    return True


def get_next_hint_time() -> str:
    now = datetime.now(tz=ZoneInfo("Australia/Sydney")) + timedelta(hours=1)
    start = config["HUNT_START_TIME"]

    if now < start:
        return "10:15 16th of March"

    time_difference = now - start
    hints_available = time_difference.seconds // SECONDS_BETWEEN_HINTS

    next_hint_time = config["HUNT_START_TIME"] + timedelta(
        hours=hints_available * 2 + (SECONDS_BETWEEN_HINTS // SECONDS_IN_AN_HOUR) - 1
    )
    return next_hint_time.strftime("%H:%M")
