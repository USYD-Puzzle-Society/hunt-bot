import discord

from functools import wraps
from typing import Coroutine

from src.queries.player import get_player
from src.queries.team import get_team


def in_team_channel(func: Coroutine) -> Coroutine:
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        interaction: discord.Interaction = args[0]
        user = interaction.user
        if not isinstance(user, discord.Member):
            return await interaction.response.send_message("Something went wrong!")
        channel = interaction.channel
        player = await get_player(user.id)

        if not player:
            return await interaction.response.send_message(
                "You must be in a team to use this command!"
            )

        team = await get_team(player.team_name)

        if team.text_channel_id != str(channel.id):
            return await interaction.response.send_message(
                "You can only use this command in your team's channel!"
            )

        return await func(self, *args, **kwargs)

    return wrapper
