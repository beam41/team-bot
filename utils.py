import discord
from discord import app_commands, Color
from db import Position, TeamMember, get_team
from env import TEAM_THREAD_PARENT_ID
from strings import *


def format_team_member(member: TeamMember, position_dict: dict[int, str]) -> str:
    pos = position_dict.get(member.pos_id) if member.pos_id else None
    pos = FORMAT_POS.format(pos) if pos else ""
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

    current = current.lower()

    return [
        app_commands.Choice(name=pos.name, value=pos.name)
        for pos in team.positions if current in pos.name.lower()
    ]

DISCORD_COLORS_MAP = {
    Color.blue.__name__: Color.blue(),
    Color.blurple.__name__: Color.blurple(),
    Color.brand_green.__name__: Color.brand_green(),
    Color.brand_red.__name__: Color.brand_red(),
    Color.dark_blue.__name__: Color.dark_blue(),
    Color.dark_embed.__name__: Color.dark_embed(),
    Color.dark_gold.__name__: Color.dark_gold(),
    Color.dark_gray.__name__: Color.dark_gray(),
    Color.dark_green.__name__: Color.dark_green(),
    Color.dark_grey.__name__: Color.dark_grey(),
    Color.dark_magenta.__name__: Color.dark_magenta(),
    Color.dark_orange.__name__: Color.dark_orange(),
    Color.dark_purple.__name__: Color.dark_purple(),
    Color.dark_red.__name__: Color.dark_red(),
    Color.dark_teal.__name__: Color.dark_teal(),
    Color.dark_theme.__name__: Color.dark_theme(),
    Color.darker_gray.__name__: Color.darker_gray(),
    Color.darker_grey.__name__: Color.darker_grey(),
    Color.fuchsia.__name__: Color.fuchsia(),
    Color.gold.__name__: Color.gold(),
    Color.green.__name__: Color.green(),
    Color.greyple.__name__: Color.greyple(),
    Color.light_embed.__name__: Color.light_embed(),
    Color.light_gray.__name__: Color.light_gray(),
    Color.light_grey.__name__: Color.light_grey(),
    Color.lighter_gray.__name__: Color.lighter_gray(),
    Color.lighter_grey.__name__: Color.lighter_grey(),
    Color.magenta.__name__: Color.magenta(),
    Color.og_blurple.__name__: Color.og_blurple(),
    Color.orange.__name__: Color.orange(),
    Color.pink.__name__: Color.pink(),
    Color.purple.__name__: Color.purple(),
    Color.random.__name__: Color.random(),
    Color.red.__name__: Color.red(),
    Color.teal.__name__: Color.teal(),
    Color.yellow.__name__: Color.yellow()
}

DISCORD_COLORS = list(DISCORD_COLORS_MAP.keys())


async def color_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    valid_color = False
    try:
        get_color(current)
        valid_color = True
    except ValueError:
        pass

    matching_colors = [
        color for color in DISCORD_COLORS if current.lower() in color]
    if valid_color:
        matching_colors.insert(0, current)

    # Limit to 25 choices as per Discord's API limit
    return [
        app_commands.Choice(name=color, value=color)
        for color in matching_colors[:25]
    ]


def get_color(color: str) -> Color:
    return Color.from_str(color if color.startswith('#') or color.lower().startswith('rgb') else f"#{color}")


def get_color_code(color: Color) -> str:
    return str(color).lstrip('#').upper()
