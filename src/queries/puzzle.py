from datetime import datetime
from typing import List
import psycopg
from psycopg.rows import class_row, dict_row

from src.config import config
from src.models.puzzle import Puzzle
from src.models.team import Team

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


async def get_puzzles_by_uni(uni: str) -> List[Puzzle]:
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor(row_factory=class_row(Puzzle))

    await acur.execute(
        """
        SELECT * FROM public.puzzles as p
        WHERE p.uni = %s
        ORDER BY p.puzzle_id ASC
        """,
        (uni,),
    )

    puzzles = await acur.fetchall()

    await acur.close()
    await aconn.close()

    return puzzles


async def get_all_puzzles() -> List[Puzzle]:
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor(row_factory=class_row(Puzzle))

    await acur.execute(
        """
        SELECT * FROM public.puzzles as p
        ORDER BY p.puzzle_id ASC
        """
    )

    puzzles = await acur.fetchall()

    await acur.close()
    await aconn.close()

    return puzzles


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


async def delete_puzzle(puzzle_id: str):
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor()

    # check existence of puzzle
    if not await get_puzzle(puzzle_id):
        return False

    await acur.execute(
        """
        DELETE FROM public.puzzles as p
        WHERE p.puzzle_id = %s
        """,
        (puzzle_id,),
    )

    await aconn.commit()
    await acur.close()
    await aconn.close()

    return True


async def get_leaderboard() -> List[tuple[str, int, datetime | None]]:
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor()
    await acur.execute("SET TIMEZONE to 'Australia/Sydney'")
    await acur.execute(
        """
        SELECT t.team_name, t.puzzle_solved, MAX(s.submission_time)
        FROM public.teams AS t LEFT JOIN public.submissions AS s
        ON (t.team_name = s.team_name)
        AND s.submission_is_correct = TRUE
        GROUP BY t.team_name
        ORDER BY t.puzzle_solved DESC, MAX(s.submission_time) ASC, t.team_name ASC
        """
    )

    leaderboard = await acur.fetchall()

    await acur.close()
    await aconn.close()

    return leaderboard


async def get_finished_teams():
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor()

    await acur.execute(
        """
        SELECT t.team_name
        FROM public.teams AS t JOIN public.submissions AS s
        ON (t.team_name = s.team_name)
        WHERE s.puzzle_id = 'METAMETA' AND s.submission_is_correct = TRUE
        """
    )

    finished_teams = await acur.fetchall()

    await acur.close()
    await aconn.close()

    return finished_teams
