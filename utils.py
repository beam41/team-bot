import discord
from discord import app_commands
from db import Position, TeamMember, get_team
from env import TEAM_THREAD_PARENT_ID
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


async def position_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    if not interaction.guild:
        return []

    if not interaction.channel or interaction.channel.type != discord.ChannelType.public_thread or (interaction.channel.parent_id != TEAM_THREAD_PARENT_ID):
        return []

    team = await get_team(interaction.guild.id, interaction.channel.id)
    if not team:
        return []

    current = current.strip().lower()

    return [
        app_commands.Choice(name=pos.name, value=pos.name)
        for pos in team.positions if current in pos.name.lower()
    ]
