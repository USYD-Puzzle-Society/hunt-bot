from typing import List
import psycopg
from psycopg.rows import class_row

from src.config import config
from src.models.puzzle import Puzzle

DATABASE_URL = config["DATABASE_URL"]


async def get_puzzle(puzzle_id: str) -> Puzzle:
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor(row_factory=class_row(Puzzle)) as acur:
            await acur.execute(
                "SELECT * FROM public.puzzles WHERE puzzle_id = %s", (puzzle_id,)
            )
            return await acur.fetchone()


async def get_puzzles() -> List[Puzzle]:
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor(row_factory=class_row(Puzzle)) as acur:
            await acur.execute("SELECT * FROM public.puzzles")
            return await acur.fetchall()


async def get_completed_puzzles(team_name: str):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor(row_factory=class_row(Puzzle)) as acur:
            await acur.execute(
                """
                SELECT p.puzzle_id, p.puzzle_name, p.puzzle_answer, p.puzzle_author, p.puzzle_link, p.uni
                FROM public.puzzles AS p
                INNER JOIN public.submissions AS s
                ON p.puzzle_id = s.puzzle_id
                WHERE s.submission_is_correct = TRUE AND s.team_name = %s
                """,
                (team_name,),
            )
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
