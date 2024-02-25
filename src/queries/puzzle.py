import psycopg
from psycopg.rows import class_row

from src.config import config
from src.models.puzzle import Puzzle

DATABASE_URL = config["DATABASE_URL"]


async def find_puzzle(puzzle_id: str):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor(row_factory=class_row(Puzzle)) as acur:
            await acur.execute(
                "SELECT * FROM public.puzzles WHERE puzzle_id = %s", (puzzle_id,)
            )
            return await acur.fetchone()
