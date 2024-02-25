import psycopg
from datetime import datetime

from src.config import config

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
