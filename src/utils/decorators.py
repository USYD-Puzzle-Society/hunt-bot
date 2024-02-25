import discord

from functools import wraps
from typing import Coroutine


def in_team_channel(func: Coroutine) -> Coroutine:
    @wraps(func)
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
        user = interaction.user
        if not isinstance(user, discord.Member):
            return await interaction.response.send_message("Something went wrong!")
        channel = interaction.channel
        # TODO: check if user is in team channel
        is_in_team_channel = True

        return func(interaction, *args, **kwargs)

    return wrapper
