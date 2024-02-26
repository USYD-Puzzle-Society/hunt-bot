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


async def find_puzzles():
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor(row_factory=class_row(Puzzle)) as acur:
            await acur.execute("SELECT * FROM public.puzzles")
            return await acur.fetchall()


async def create_puzzle(
    puzzle_id: str,
    puzzle_name: str,
    puzzle_answer: str,
    puzzle_author: str,
    puzzle_link: str,
    uni: str,
):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor() as acur:
            await acur.execute(
                """ 
                INSERT INTO public.puzzles 
                (puzzle_id, puzzle_name, puzzle_answer, puzzle_author, puzzle_link, uni)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    puzzle_id,
                    puzzle_name,
                    puzzle_answer,
                    puzzle_author,
                    puzzle_link,
                    uni,
                ),
            )
