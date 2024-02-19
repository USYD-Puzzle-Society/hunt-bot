import discord
from discord.ext import commands
from discord import app_commands

class Answers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.answers = {
            "Straight As": "wakawaka",
            "47 Black Sheep": "not hitting women",
            "A Solid Plan": "hard",
            "God's Kitchen": "what's the opposite of gordon ramsay",
            "Librinth": "books idk",
            "Susharks in the Wafer": "i'm kinda hungry",
            "We Need to Eat": "aaaaaaaaanoodl"
        }

    @app_commands.command(name="check")
    # remember to add a check so that users can only check answers in their respective
    # team channels
    async def check_answer(self, puzz_name: str, answer: str):
        pass