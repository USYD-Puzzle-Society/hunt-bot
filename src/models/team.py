from dataclasses import dataclass


@dataclass
class Team:
    team_name: str
    category_channel_id: str
    voice_channel_id: str
    text_channel_id: str
    team_role_id: str
    puzzle_solved: int
