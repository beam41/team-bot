from db import Position, TeamMember
from strings import *


def format_team_member(member: TeamMember, position_dict: dict[int, str]) -> str:
    pos = position_dict.get(member.pos_id) if member.pos_id else None
    pos = f" - {pos}" if pos else ""
    return FORMAT_TEAM_MEMBER.format(member.number, member.id, pos)


def format_team_members(members: list[TeamMember], positions: list[Position]) -> str:
    # convert position to dictionary for quick lookup
    position_dict = {position.id: position.name for position in positions}
    return "\n".join(format_team_member(member, position_dict) for member in members)


def format_bool_yes_no(value: bool):
    """Convert a boolean value to 'Yes' or 'No' string."""
    return BOOL_YES if value else BOOL_NO
