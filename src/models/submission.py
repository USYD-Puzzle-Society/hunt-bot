from dataclasses import dataclass
from datetime import datetime


@dataclass
class Submission:
    puzzle_id: str
    team_name: str
    submission_time: datetime
    submission_answer: str
    submission_is_correct: bool
