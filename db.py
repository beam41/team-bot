from dataclasses import dataclass
import json


@dataclass
class Team:
    thread_id: int
    owner_id: int
    role_id: int | None
    name: str
    tag: str
    color: str
    auto_accept: bool
    member: list[int]
    reason: str


# simple read/write can be replace with a database later
async def write(guild: int, teams: list[Team]):
    with open(f'teams-{guild}.json', 'w') as file:
        file.write(json.dumps([t.__dict__ for t in teams]))


async def read(guild: int) -> list[Team]:
    with open(f'teams-{guild}.json', 'r') as file:
        return [Team(**team) for team in json.loads(file.read())]


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
