import discord
from discord.ext import commands
from discord import app_commands, User, Member

from src.context.puzzle import find_puzzle


class Puzzle(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="submit", description="Submit an answer to a puzzle")
    async def submit_answer(
        self, interaction: discord.Interaction, puzzle_id: str, answer: str
    ):
        if not await self.is_in_team_channel(interaction.user):
            await interaction.response.send_message(
                "You can only use this command in your team's channel!", ephemeral=True
            )
            return

        puzzle = await find_puzzle(puzzle_id)

    @app_commands.command(name="list", description="List the available puzzles")
    async def list_puzzles(self, interaction: discord.Interaction):
        pass

    async def is_in_team_channel(user: User | Member) -> bool:
        # TODO
        return True


async def setup(bot: commands.Bot):
    await bot.add_cog(Puzzle(bot))
