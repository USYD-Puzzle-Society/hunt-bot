from typing import List
from src.models.puzzle import Puzzle
from src.queries.puzzle import find_puzzles

NUMBER_OF_FEEDERS = {"UTS": 4, "UNSW": 4, "USYD": 6}


async def can_access_puzzle(puzzle: Puzzle, discord_id: int) -> bool:
    pass


async def get_accessible_puzzles(discord_id: int) -> List[Puzzle]:
    # TODO: implementation
    puzzles = await find_puzzles()
    return puzzles
