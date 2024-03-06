import discord

from src.queries.player import get_player, remove_player
from src.queries.team import get_team, get_team_members, remove_team


# kicked: a True/False value that lets the function know whether the member
# is leaving the team on their own or is being kicked from the team by
# an admin
async def remove_member_from_team(
    interaction: discord.Interaction, member: discord.Member, kicked: bool
):
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild

    # get player object from member
    player = await get_player(str(member.id))

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

    team = await get_team(team_name)
    team_role_id = int(team.team_role_id)
    role = guild.get_role(team_role_id)

    # remove their team role
    await member.remove_roles(role)

    # delete player
    await remove_player(str(member.id))

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

    category_channel = guild.get_channel(int(team.category_channel_id))
    text_channel = guild.get_channel(int(team.text_channel_id))
    voice_channel = guild.get_channel(int(team.voice_channel_id))

    # delete roles and channels
    await text_channel.delete()
    await voice_channel.delete()
    await category_channel.delete()
    await role.delete()

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
