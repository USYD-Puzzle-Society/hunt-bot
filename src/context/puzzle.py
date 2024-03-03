from typing import List
from src.models.puzzle import Puzzle
from src.queries.puzzle import get_puzzles, get_completed_puzzles
from src.queries.player import get_player

NUMBER_OF_FEEDERS = {"UTS": 4, "UNSW": 4, "USYD": 6}


# the meat of the context. given a puzzle and a list of completed puzzle, determine if the puzzle is accessible yet
# current logic:
# all puzzles in a round are unlocked if the previous meta is completed (UTS is unlocked by default)
# order is UTS -> USYD -> UNSW
# solver must have solved all feeders to get the meta
# all meta solved to get the metameta
def can_access_puzzle_context(puzzle: Puzzle, completed_puzzles: List[Puzzle]) -> bool:
    if puzzle.uni == "UTS" and puzzle.puzzle_id != "UTS-M":
        return True

    if (
        puzzle.puzzle_id == "UTS-M"
        and len([puzzle for puzzle in completed_puzzles if puzzle.uni == "UTS"])
        >= NUMBER_OF_FEEDERS["UTS"]
    ):
        return True

    if (
        puzzle.uni == "USYD"
        and puzzle.puzzle_id != "USYD-M"
        and any([puzzle.puzzle_id == "UTS-M" for puzzle in completed_puzzles])
    ):
        return True

    if (
        puzzle.puzzle_id == "USYD-M"
        and len([puzzles for puzzles in completed_puzzles if puzzle.uni == "USYD"])
        >= NUMBER_OF_FEEDERS["USYD"]
    ):
        return True

    if (
        puzzle.uni == "UNSW"
        and puzzle.puzzle_id != "UNSW-M"
        and any([puzzle.puzzle_id == "USYD-M" for puzzle in completed_puzzles])
    ):
        return True

    if (
        puzzle.puzzle_id == "UNSW-M"
        and len([puzzles for puzzles in completed_puzzles if puzzle.uni == "UNSW"])
        >= NUMBER_OF_FEEDERS["UNSW"]
    ):
        return True

    if puzzle.puzzle_id == "METAMETA" and any(
        [puzzle.puzzle_id == "UNSW-M" for puzzle in completed_puzzles]
    ):
        return True

    return False


async def can_access_puzzle(puzzle: Puzzle, team_name: str) -> bool:
    return can_access_puzzle_context(puzzle, await get_completed_puzzles(team_name))


async def get_accessible_puzzles(team_name: str) -> List[Puzzle]:
    puzzles = await get_puzzles()
    completed_puzzles = await get_completed_puzzles(team_name)
    return [
        puzzle
        for puzzle in puzzles
        if can_access_puzzle_context(puzzle, completed_puzzles)
    ]
