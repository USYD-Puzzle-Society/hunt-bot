import pytest
import pytest_asyncio

from tests.utils import truncate
from src.queries.puzzle import create_puzzle, find_puzzle
from src.models.puzzle import Puzzle


class TestClass:
    @pytest_asyncio.fixture(autouse=True)
    async def async_setup(self):
        await truncate()
        yield

    @pytest.mark.asyncio
    async def test_can_create_puzzle(self):
        expected: Puzzle = Puzzle(
            "UTS-1", "The Answer of Life", "42", "Skelly", "tiny.cc/rickroll", "UTS"
        )
        await create_puzzle(
            expected.puzzle_id,
            expected.puzzle_name,
            expected.puzzle_answer,
            expected.puzzle_author,
            expected.puzzle_link,
            expected.uni,
        )
        result = await find_puzzle("UTS-1")
        assert expected == result
