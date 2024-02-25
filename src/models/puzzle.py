from dataclasses import dataclass


@dataclass
class Puzzle:
    puzzle_id: str
    puzzle_name: str
    puzzle_answer: str
    puzzle_author: str
    puzzle_link: str
    uni: str
