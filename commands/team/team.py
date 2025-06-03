from typing import Optional
from commands.ui.unregister_team import UnregisterTeamConfirmButton
from env import TEAM_THREAD_PARENT_ID
from db import Position, Team, TeamMember, add_team, get_team, load_team, remove_team
from utils import format_team_members, format_bool_yes_no
import discord
from discord import app_commands
import re
import time
from strings import *

# Create the command group
group = app_commands.Group(
    name=TEAM_CMD_GROUP, description=TEAM_CMD_GROUP_DESC)


@group.command(name=REGISTER_TEAM_CMD, description=REGISTER_TEAM_CMD_DESC)
@app_commands.describe(
    name=REGISTER_TEAM_CMD_NAME_DESC,
    tag=REGISTER_TEAM_CMD_TAG_DESC,
    team_color=REGISTER_TEAM_CMD_TEAM_COLOR_DESC,
    auto_accept=REGISTER_TEAM_CMD_AUTO_ACCEPT_DESC,
    reason_placeholder=REGISTER_TEAM_CMD_REASON_PLACEHOLDER_DESC,
    skip_make_role=REGISTER_TEAM_CMD_SKIP_MAKE_ROLE_DESC,
    positions=REGISTER_TEAM_CMD_POSITION_DESC
)
async def register_team(interaction: discord.Interaction, name: str, tag: str, team_color: str, auto_accept: bool, reason_placeholder: str, positions: Optional[str], skip_make_role: Optional[bool]) -> None:
    if not interaction.guild:
        await interaction.response.send_message(GUILD_ONLY_ERR, ephemeral=True)
        return

    if not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message(MEMBERS_ONLY_ERR, ephemeral=True)
        return

    if not interaction.channel or interaction.channel.type != discord.ChannelType.public_thread or (interaction.channel.parent_id != TEAM_THREAD_PARENT_ID):
        await interaction.response.send_message(TEAM_THREADS_ONLY_ERR, ephemeral=True)
        return

    if interaction.channel.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(THREAD_OWNER_OR_ADMIN_ERR, ephemeral=True)
        return

    # Clean up and validate inputs
    name = name.strip()
    tag = tag.upper().strip()
    team_color = team_color.lstrip('#').upper()

    if team_color and not re.match(HEX_COLOR_PATTERN, team_color):
        await interaction.response.send_message(INVALID_COLOR_ERR, ephemeral=True)
        return

    if not re.match(TEAM_TAG_PATTERN, tag):
        await interaction.response.send_message(INVALID_TAG_ERR, ephemeral=True)
        return

    # Check if the thread already has a team
    team = await get_team(interaction.guild.id, interaction.channel.id)
    if team:
        await interaction.response.send_message(TEAM_ALREADY_REGISTERED_ERR, ephemeral=True)
        return

    # Check if the name or tag already exists
    teams = await load_team(interaction.guild.id)
    for team in teams:
        if team.name == name or team.tag == tag:
            await interaction.response.send_message(TEAM_NAME_OR_TAG_EXISTS_ERR, ephemeral=True)
            return

    # Create team role if not skipped
    role_id = None
    embeds = []
    if not skip_make_role:
        try:
            hex_color = int(team_color or "FFFFFF", 16)
            role = await interaction.guild.create_role(
                name=tag,
                color=discord.Color(hex_color),
                reason=f"Team {name} creation"
            )
            role_id = role.id

            # Assign role to user
            try:
                await interaction.user.add_roles(role)
            except discord.Forbidden:
                embeds.append(
                    discord.Embed(
                        title=ROLE_ASSIGNMENT_FAILED_TITLE,
                        description=ROLE_ASSIGNMENT_FAILED_DESC_PERMISSION,
                        color=discord.Color.red()
                    )
                )
            except discord.HTTPException as e:
                embeds.append(
                    discord.Embed(
                        title=ROLE_ASSIGNMENT_FAILED_TITLE,
                        description=ROLE_ASSIGNMENT_FAILED_DESC_FAILED.format(
                            e),
                        color=discord.Color.red()
                    )
                )

        except discord.Forbidden:
            embeds.append(
                discord.Embed(
                    title=ROLE_CREATION_FAILED_TITLE,
                    description=ROLE_CREATION_FAILED_DESC_PERMISSION,
                    color=discord.Color.red()
                )
            )
        except discord.HTTPException as e:
            embeds.append(
                discord.Embed(
                    title=ROLE_CREATION_FAILED_TITLE,
                    description=ROLE_CREATION_FAILED_DESC_FAILED.format(e),
                    color=discord.Color.red()
                )
            )

    # Process positions
    team_positions = []
    if positions:
        pos_list = [p for pos in positions.split(',') if (p := pos.strip())]
        if len(pos_list) > MAX_POSITIONS:
            await interaction.response.send_message(
                TOO_MANY_POSITIONS_ERR, ephemeral=True)
            return
        for idx, pos_name in enumerate(pos_list):
            # Use Unix timestamp + index as position ID
            pos_id = int(time.time()) + idx
            team_positions.append(Position(id=pos_id, name=pos_name))

    # Create member
    owner_member = TeamMember(id=interaction.user.id, number=0)

    # Create and save the team
    new_team = Team(
        thread_id=interaction.channel.id,
        owner_id=interaction.user.id,
        role_id=role_id,
        name=name,
        tag=tag,
        color=team_color or "FFFFFF",
        auto_accept=auto_accept,
        members=[owner_member],
        reason=reason_placeholder,
        positions=team_positions
    )

    await add_team(interaction.guild.id, new_team)

    # Create success embed
    embed = discord.Embed(
        title=TEAM_REGISTERED_TITLE,
        description=TEAM_REGISTERED_DESC.format(name, tag),
        color=discord.Color.green()
    )
    embed.add_field(name=TEAM_REGISTERED_FIELD_OWNER, value=FORMAT_USER_MENTION.format(
        interaction.user.id), inline=True)

    if role_id:
        embed.add_field(name=TEAM_REGISTERED_FIELD_ROLE,
                        value=FORMAT_ROLE_MENTION.format(role_id), inline=True)
    else:
        embed.add_field(name=TEAM_REGISTERED_FIELD_ROLE,
                        value=ROLE_NO_ROLE_CREATED, inline=True)

    embed.add_field(name=TEAM_REGISTERED_FIELD_TEAM_COLOR, value=FORMAT_TEAM_COLOR_DISPLAY.format(
        new_team.color), inline=True)
    embed.add_field(name=TEAM_REGISTERED_FIELD_AUTO_ACCEPT,
                    value=format_bool_yes_no(auto_accept), inline=True)

    # Add positions field if any
    if team_positions:
        positions_text = "\n".join(p.name for p in team_positions)
        embed.add_field(name=TEAM_DETAILS_FIELD_AVAILABLE_POSITIONS,
                        value=positions_text, inline=False)

    embeds.append(embed)
    await interaction.response.send_message(embeds=embeds, silent=True)


@group.command(name=UNREGISTER_TEAM_CMD, description=UNREGISTER_TEAM_CMD_DESC)
async def unregister_team(interaction: discord.Interaction) -> None:
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
        await interaction.response.send_message(TEAM_OWNER_OR_ADMIN_ERR, ephemeral=True)
        return

    embed = discord.Embed(
        title=UNREGISTER_TEAM_CONFIRMATION_TITLE,
        description=UNREGISTER_TEAM_CONFIRMATION_DESC,
        color=discord.Color.blue()
    )
    button = UnregisterTeamConfirmButton()
    await interaction.response.send_message(embed=embed, view=button, ephemeral=True)


@group.command(name=TEAM_DETAILS_CMD, description=TEAM_DETAILS_CMD_DESC)
async def team_details(interaction: discord.Interaction) -> None:
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

    # Format members
    members = format_team_members(team.members, team.positions)

    # Create embed
    embed = discord.Embed(
        title=TEAM_DETAILS_TITLE,
        description=TEAM_DETAILS_DESC.format(team.name, team.tag),
        color=discord.Color.blue()
    )
    embed.add_field(name=TEAM_DETAILS_FIELD_OWNER, value=FORMAT_USER_MENTION.format(
        team.owner_id), inline=True)
    embed.add_field(
        name=TEAM_REGISTERED_FIELD_ROLE, value=FORMAT_ROLE_MENTION.format(team.role_id) if team.role_id else ROLE_NO_ROLE, inline=True)
    embed.add_field(name=TEAM_REGISTERED_FIELD_TEAM_COLOR, value=FORMAT_TEAM_COLOR_DISPLAY.format(
        team.color), inline=True)
    embed.add_field(name=TEAM_REGISTERED_FIELD_AUTO_ACCEPT,
                    value=format_bool_yes_no(team.auto_accept), inline=True)

    embed.add_field(name=TEAM_DETAILS_FIELD_MEMBERS,
                    value=members, inline=False)

    # Add positions field if any
    if team.positions:
        positions_text = "\n".join(p.name for p in team.positions)
        embed.add_field(name=TEAM_DETAILS_FIELD_AVAILABLE_POSITIONS,
                        value=positions_text, inline=False)

    await interaction.response.send_message(embed=embed, silent=True, ephemeral=True)
