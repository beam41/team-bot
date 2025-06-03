from dataclasses import dataclass
import json
from typing import Optional

TEAMS_FILE_TEMPLATE = "teams-{}.json"


@dataclass
class Position:
    id: int
    name: str


@dataclass
class TeamMember:
    id: int
    number: int
    pos_id: Optional[int] = None


@dataclass
class Team:
    thread_id: int
    owner_id: int
    role_id: Optional[int]
    name: str
    tag: str
    color: str
    auto_accept: bool
    members: list[TeamMember]
    reason: str
    positions: list[Position]


# simple read/write can be replace with a database later
async def write(guild: int, teams: list[Team]):
    with open(TEAMS_FILE_TEMPLATE.format(guild), 'w') as file:
        teams_data = []
        for team in teams:
            team_dict = team.__dict__.copy()
            team_dict['members'] = [
                member.__dict__ for member in team.members]
            team_dict['positions'] = [
                position.__dict__ for position in team.positions]
            teams_data.append(team_dict)
        file.write(json.dumps(teams_data))


async def read(guild: int) -> list[Team]:
    with open(TEAMS_FILE_TEMPLATE.format(guild), 'r') as file:
        data = json.loads(file.read())
        teams = []
        for team_data in data:
            team_data['members'] = [TeamMember(
                **m) for m in team_data['members']]
            team_data['positions'] = [Position(
                **p) for p in team_data['positions']]
            teams.append(Team(**team_data))
        return teams


async def load_team(guild: int):
    teams = await read(guild)
    return teams


async def get_team(guild: int, thread_id: int):
    teams = await load_team(guild)
    for team in teams:
        if team.thread_id == thread_id:
            return Team(**team.__dict__)
    return None


async def add_team(guild: int, team: Team):
    teams = await load_team(guild)
    teams.append(team)
    await write(guild, teams)
    return teams


async def remove_team(guild: int, thread_id: int):
    teams = await load_team(guild)
    teams = [team for team in teams if team.thread_id != thread_id]
    await write(guild, teams)
    return teams


async def update_team(guild: int, team: Team):
    teams = await load_team(guild)
    for i, t in enumerate(teams):
        if t.thread_id == team.thread_id:
            teams[i] = team
            break
    await write(guild, teams)
    return teams
