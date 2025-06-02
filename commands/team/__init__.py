# Team commands package
from .management import register_team, unregister_team, team_details
from .updates import group as update_team_group
from .members import join_team, leave_team, add_team_member, remove_team_member

__all__ = [
    'register_team',
    'unregister_team',
    'team_details',
    'update_team_group',
    'join_team',
    'leave_team',
    'add_team_member',
    'remove_team_member'
]
