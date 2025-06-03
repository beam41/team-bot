from env import TEAM_THREAD_PARENT_ID
from db import Position, get_team, update_team
import discord
from discord import app_commands
import time
from strings import *
from utils import position_autocomplete
from .update_team import group as update_team_group

group = app_commands.Group(name="position",
                           description=UPDATE_POSITION_CMD_GROUP_DESC,
                           parent=update_team_group)


@group.command(name=ADD_POSITION_CMD, description=ADD_POSITION_CMD_DESC)
@app_commands.describe(position=ADD_POSITION_CMD_POSITION_DESC)
async def add_position(interaction: discord.Interaction, position: str) -> None:
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

    if team.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(TEAM_OWNER_OR_ADMIN_POSITION_ERR, ephemeral=True)
        return

    # Check if the maximum number of positions has been reached
    if len(team.positions) >= MAX_POSITIONS:
        await interaction.response.send_message(MAX_POSITIONS_ERR, ephemeral=True)
        return

    # Validate position name
    if not position:
        await interaction.response.send_message(POSITION_NAME_EMPTY_ERR, ephemeral=True)
        return

    existing_position = next(
        (p for p in team.positions if p.name == position), None)
    if existing_position:
        await interaction.response.send_message(POSITION_ALREADY_EXISTS_ERR, ephemeral=True)
        return

    # Use Unix timestamp as position ID
    position_id = int(time.time())
    new_position = Position(id=position_id, name=position)

    # Add the new position to the team
    team.positions.append(new_position)
    await update_team(interaction.guild.id, team)

    # Create success embed
    embed = discord.Embed(
        title=POSITION_ADDED_TITLE,
        description=POSITION_ADDED_DESC.format(position, team.name, team.tag),
        color=discord.Color.green()
    )
    # Add current positions field
    if team.positions:
        positions_list = "\n".join(p.name for p in team.positions)
        embed.add_field(
            name=POSITION_ADDED_FIELD_CURRENT_POSITIONS,
            value=positions_list,
            inline=False
        )

    await interaction.response.send_message(embed=embed, silent=True)


@group.command(name=EDIT_POSITION_CMD, description=EDIT_POSITION_CMD_DESC)
@app_commands.describe(
    position=EDIT_POSITION_CMD_POSITION_DESC,
    new_position=EDIT_POSITION_CMD_NEW_POSITION_DESC
)
@app_commands.autocomplete(position=position_autocomplete)
async def edit_position(interaction: discord.Interaction, position: str, new_position: str) -> None:
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

    if team.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(TEAM_OWNER_OR_ADMIN_POSITION_ERR, ephemeral=True)
        return

    # Validate new position name
    if not new_position:
        await interaction.response.send_message(POSITION_NAME_EMPTY_ERR, ephemeral=True)
        return

    position_to_edit = next(
        (p for p in team.positions if p.name == position), None)
    if not position_to_edit:
        await interaction.response.send_message(POSITION_NOT_FOUND_ERR, ephemeral=True)
        return

    existing_position = next((p for p in team.positions if p.name ==
                             new_position and p.id != position_to_edit.id), None)
    if existing_position:
        await interaction.response.send_message(POSITION_ALREADY_EXISTS_ERR, ephemeral=True)
        return

    # Store old name for the embed
    old_name = position_to_edit.name

    # Update the position name
    position_to_edit.name = new_position
    await update_team(interaction.guild.id, team)

    # Create success embed
    embed = discord.Embed(
        title=POSITION_UPDATED_TITLE,
        description=POSITION_UPDATED_DESC.format(
            old_name, new_position, team.name, team.tag),
        color=discord.Color.green()
    )

    # Add current positions field
    if team.positions:
        positions_list = "\n".join(p.name for p in team.positions)
        embed.add_field(
            name=POSITION_UPDATED_FIELD_CURRENT_POSITIONS,
            value=positions_list,
            inline=False
        )

    await interaction.response.send_message(embed=embed, silent=True)


@group.command(name=DELETE_POSITION_CMD, description=DELETE_POSITION_CMD_DESC)
@app_commands.describe(position=DELETE_POSITION_CMD_POSITION_DESC)
@app_commands.autocomplete(position=position_autocomplete)
async def delete_position(interaction: discord.Interaction, position: str) -> None:
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

    if team.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(TEAM_OWNER_OR_ADMIN_POSITION_ERR, ephemeral=True)
        return

    position_to_delete = next(
        (p for p in team.positions if p.name == position), None)

    if not position_to_delete:
        await interaction.response.send_message(POSITION_NOT_FOUND_ERR, ephemeral=True)
        return

    # Store the name for the embed
    deleted_name = position_to_delete.name

    # Remove the position from the team
    team.positions = [
        p for p in team.positions if p.id != position_to_delete.id]
    await update_team(interaction.guild.id, team)

    # Create success embed
    embed = discord.Embed(
        title=POSITION_DELETED_TITLE,
        description=POSITION_DELETED_DESC.format(
            deleted_name, team.name, team.tag),
        color=discord.Color.green()
    )
    if len(team.positions):
        positions_list = "\n".join(p.name for p in team.positions)
        embed.add_field(
            name=POSITION_DELETED_FIELD_CURRENT_POSITIONS,
            value=positions_list,
            inline=False
        )
    else:
        embed.add_field(
            name=POSITION_DELETED_FIELD_CURRENT_POSITIONS,
            value=POSITIONS_NO_POSITIONS,
            inline=False
        )

    await interaction.response.send_message(embed=embed, silent=True)
