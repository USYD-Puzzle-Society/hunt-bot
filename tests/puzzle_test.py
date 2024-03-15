from datetime import datetime
from zoneinfo import ZoneInfo
import pytest
import pytest_asyncio

from tests.utils import truncate
from src.queries.puzzle import create_puzzle, get_puzzle, get_leaderboard
from src.queries.team import create_team, increase_puzzles_solved
from src.queries.submission import create_submission
from src.models.puzzle import Puzzle


class TestClass:
    @pytest_asyncio.fixture(autouse=True)
    async def async_setup(self):
        await truncate()
        yield

    @pytest.mark.asyncio
    async def test_can_create_puzzle(self):
        expected: Puzzle = Puzzle(
            "UTS-01", "The Answer of Life", "42", "Skelly", "tiny.cc/rickroll", "UTS"
        )
        await create_puzzle(
            expected.puzzle_id,
            expected.puzzle_name,
            expected.puzzle_answer,
            expected.puzzle_author,
            expected.puzzle_link,
            expected.uni,
        )
        result = await get_puzzle("UTS-01")
        assert expected == result

    @pytest.mark.asyncio
    async def test_empty_leaderboard(self):
        await create_puzzle(
            "UTS-01",
            "The Answer of Life",
            "42",
            "Skelly",
            "tiny.cc/rickroll",
            "UTS",
        )
        await create_team("test team", 1, 1, 1, 1)
        assert await get_leaderboard() == [("test team", 0, None)]

    @pytest.mark.asyncio
    async def test_leaderboard(self):
        await create_puzzle(
            "UTS-01",
            "The Answer of Life",
            "42",
            "Skelly",
            "tiny.cc/rickroll",
            "UTS",
        )
        await create_team("test team 1", 1, 1, 1, 1)
        await create_team("test team 2", 1, 1, 1, 1)

        await create_submission(
            "UTS-01",
            "test team 2",
            datetime(2024, 1, 1, tzinfo=ZoneInfo("Australia/Sydney")),
            "42",
            True,
        )

        await increase_puzzles_solved("test team 2")

        assert await get_leaderboard() == [
            (
                "test team 2",
                1,
                datetime(2024, 1, 1, tzinfo=ZoneInfo("Australia/Sydney")),
            ),
            ("test team 1", 0, None),
        ]
