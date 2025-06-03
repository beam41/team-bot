from env import TEAM_THREAD_PARENT_ID
from db import get_team, update_team
from utils import format_team_members
import discord
from discord import Member, app_commands
from typing import Optional
from strings import *
from .update_member import group as update_member_group

# Create the command group
group = app_commands.Group(name=UPDATE_MEMBER_INFO_CMD_GROUP,
                           description=UPDATE_MEMBER_INFO_CMD_GROUP_DESC,
                           parent=update_member_group)


@group.command(name=CHANGE_PLAYER_NUMBER_CMD, description=CHANGE_PLAYER_NUMBER_CMD_DESC)
@app_commands.describe(
    new_number=CHANGE_PLAYER_NUMBER_CMD_NEW_NUMBER_DESC,
    member=CHANGE_PLAYER_NUMBER_CMD_MEMBER_DESC,
)
async def change_player_number(interaction: discord.Interaction, new_number: int, member: Optional[Member]) -> None:
    if not interaction.guild:
        await interaction.response.send_message(GUILD_ONLY_ERR, ephemeral=True)
        return

    if not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message(MEMBERS_ONLY_ERR, ephemeral=True)
        return

    if not interaction.channel or interaction.channel.type != discord.ChannelType.public_thread or (interaction.channel.parent_id != TEAM_THREAD_PARENT_ID):
        await interaction.response.send_message(TEAM_THREADS_ONLY_ERR, ephemeral=True)
        return

    team = await get_team(interaction.guild.id, interaction.channel.id)
    if not team:
        await interaction.response.send_message(NO_TEAM_REGISTERED_ERR, ephemeral=True)
        return

    if member is None:
        member = interaction.user
    else:
        if team.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(TEAM_OWNER_OR_ADMIN_CHANGE_NUMBER_ERR, ephemeral=True)
            return

    # Validate player number
    if new_number < 0 or new_number > 99:
        await interaction.response.send_message(PLAYER_NUMBER_RANGE_ERR, ephemeral=True)
        return

    # Check if the member is in the team
    team_member = None
    for tm in team.members:
        if tm.id == member.id:
            team_member = tm
            break

    if not team_member:
        await interaction.response.send_message(USER_NOT_MEMBER_ERR, ephemeral=True)
        return

    # Store the old number for display
    old_number = team_member.number

    # Update the member's number
    team_member.number = new_number
    await update_team(interaction.guild.id, team)

    # Create success embed
    embed = discord.Embed(
        title=PLAYER_NUMBER_CHANGED_TITLE,
        description=PLAYER_NUMBER_CHANGED_DESC.format(
            member.id, old_number, new_number, team.name, team.tag),
        color=discord.Color.green()
    )

    # Show updated member list
    members = format_team_members(team.members, team.positions)
    embed.add_field(name=TEAM_MEMBER_REMOVED_FIELD_CURRENT_MEMBERS,
                    value=members, inline=False)

    await interaction.response.send_message(embed=embed, silent=True)


@group.command(name=CHANGE_POSITION_CMD, description=CHANGE_POSITION_CMD_DESC)
@app_commands.describe(
    position=CHANGE_POSITION_CMD_POSITION_DESC,
    member=CHANGE_POSITION_CMD_MEMBER_DESC
)
async def change_position(interaction: discord.Interaction, position: str, member: Optional[Member]) -> None:
    if not interaction.guild:
        await interaction.response.send_message(GUILD_ONLY_ERR, ephemeral=True)
        return

    if not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message(MEMBERS_ONLY_ERR, ephemeral=True)
        return

    if not interaction.channel or interaction.channel.type != discord.ChannelType.public_thread or (interaction.channel.parent_id != TEAM_THREAD_PARENT_ID):
        await interaction.response.send_message(TEAM_THREADS_ONLY_ERR, ephemeral=True)
        return

    team = await get_team(interaction.guild.id, interaction.channel.id)
    if not team:
        await interaction.response.send_message(NO_TEAM_REGISTERED_ERR, ephemeral=True)
        return

    if member is None:
        member = interaction.user
    else:
        if team.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(TEAM_OWNER_OR_ADMIN_CHANGE_POSITION_ERR, ephemeral=True)
            return

    # Check if the position exists in the team
    position_obj = None
    for pos in team.positions:
        if pos.name.lower() == position.lower():
            position_obj = pos
            break

    if not position_obj:
        await interaction.response.send_message(POSITION_NOT_FOUND_ERR, ephemeral=True)
        return

    # Check if the member is in the team
    team_member = None
    for tm in team.members:
        if tm.id == member.id:
            team_member = tm
            break

    if not team_member:
        await interaction.response.send_message(USER_NOT_MEMBER_ERR, ephemeral=True)
        return

    # Store the old position for display
    old_position_id = team_member.pos_id
    old_position_name = "None"
    if old_position_id:
        for pos in team.positions:
            if pos.id == old_position_id:
                old_position_name = pos.name
                break

    # Update the member's position
    team_member.pos_id = position_obj.id
    await update_team(interaction.guild.id, team)

    # Create success embed
    embed = discord.Embed(
        title=PLAYER_POSITION_CHANGED_TITLE,
        description=PLAYER_POSITION_CHANGED_DESC.format(
            member.id, old_position_name, position_obj.name, team.name, team.tag),
        color=discord.Color.green()
    )

    # Show updated member list
    members = format_team_members(team.members, team.positions)
    embed.add_field(name=TEAM_MEMBER_REMOVED_FIELD_CURRENT_MEMBERS,
                    value=members, inline=False)

    await interaction.response.send_message(embed=embed, silent=True)
