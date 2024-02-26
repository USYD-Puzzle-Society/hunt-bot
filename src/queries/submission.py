import psycopg
from psycopg.rows import class_row
from datetime import datetime

from src.config import config
from src.models.submission import Submission

DATABASE_URL = config["DATABASE_URL"]


async def create_submission(
    puzzle_id: str,
    team_name: str,
    submission_time: datetime,
    submission_answer: str,
    submission_is_correct: bool,
):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor() as acur:
            await acur.execute(
                """
                INSERT INTO public.submissions 
                (puzzle_id, team_name, submission_time, submission_answer, submission_is_correct) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    puzzle_id,
                    team_name,
                    submission_time,
                    submission_answer,
                    submission_is_correct,
                ),
            )


async def find_submissions_by_player_id(player_id: str):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor(row_factory=class_row(Submission)) as acur:
            await acur.execute(
                """
                SELECT s.puzzle_id, s.team_name, s.submission_time, s.submission_answer, s.submission_is_correct
                FROM public.submissions AS s
                INNER JOIN public.teams AS t ON t.team_name = s.team_name
                INNER JOIN public.players AS p ON p.team_name = t.team_name
                WHERE p.discord_id = %s  
                """,
                (player_id,),
            )

            return await acur.fetchall()


async def find_submissions_by_team(team_name: str):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor(row_factory=class_row(Submission)) as acur:
            await acur.execute(
                "SELECT * FROM public.submissions WHERE team_name = %s",
                (team_name,),
            )

            return await acur.fetchall()
