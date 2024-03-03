from typing import List
from src.models.puzzle import Puzzle
from src.queries.puzzle import get_puzzles, get_completed_puzzles
from src.queries.player import get_player

NUMBER_OF_FEEDERS = {"UTS": 4, "UNSW": 4, "USYD": 6}


# the meat of the context. given a puzzle and a list of completed puzzle, determine if the puzzle is accessible yet
# current logic: solver must have solved all feeders to get the meta
# all meta solved to get the metameta
def can_access_puzzle_context(puzzle: Puzzle, completed_puzzles: List[Puzzle]) -> bool:
    return True


async def can_access_puzzle(puzzle: Puzzle, discord_id: int) -> bool:
    player = await get_player(str(discord_id))
    return can_access_puzzle_context(
        puzzle, await get_completed_puzzles(player.team_name)
    )


async def get_accessible_puzzles(discord_id: int) -> List[Puzzle]:
    puzzles = await get_puzzles()
    player = await get_player(str(discord_id))
    completed_puzzles = await get_completed_puzzles(player.team_name)
    return [
        puzzle
        for puzzle in puzzles
        if can_access_puzzle_context(puzzle, completed_puzzles)
    ]
