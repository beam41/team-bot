from env import TEAM_THREAD_PARENT_ID
from db import get_team, load_team, update_team
from utils import format_bool_yes_no
import discord
from discord import Member, Role, app_commands
import re
from typing import Optional
from strings import *

group = app_commands.Group(name=UPDATE_TEAM_CMD_GROUP,
                           description=UPDATE_TEAM_CMD_GROUP_DESC)


async def update_team_common(interaction: discord.Interaction, *, name: Optional[str] = None, tag: Optional[str] = None, color: Optional[str] = None, owner: Optional[Member] = None, auto_accept: Optional[bool] = None, reason: Optional[str] = None, link_role: Optional[Role] = None) -> None:
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

    if link_role:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(ADMIN_ONLY_UPDATE_ERR, ephemeral=True)
            return
    else:
        if team.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(TEAM_OWNER_OR_ADMIN_UPDATE_ERR, ephemeral=True)
            return

    embeds = []

    if name is not None:
        name = name.strip()
        teams = await load_team(interaction.guild.id)
        for t in teams:
            if t.name == name:
                await interaction.response.send_message(TEAM_NAME_EXISTS_ERR, ephemeral=True)
                return
        team.name = name

    if tag is not None:
        if not re.match(TEAM_TAG_PATTERN, tag):
            await interaction.response.send_message(INVALID_TAG_ERR, ephemeral=True)
            return
        teams = await load_team(interaction.guild.id)
        for t in teams:
            if t.tag == tag:
                await interaction.response.send_message(TEAM_TAG_EXISTS_ERR, ephemeral=True)
                return
        team.tag = tag
        # Update role name if exists
        if team.role_id:
            role = interaction.guild.get_role(team.role_id)
            if role:
                try:
                    await role.edit(name=team.tag)
                except (discord.Forbidden, discord.HTTPException) as e:
                    embeds.append(
                        discord.Embed(
                            title=ROLE_UPDATE_FAILED_TITLE,
                            description=ROLE_UPDATE_FAILED_DESC.format(e),
                            color=discord.Color.red()
                        )
                    )

    if color is not None:
        color = color.lstrip('#').upper()
        if not re.match(HEX_COLOR_PATTERN, color):
            await interaction.response.send_message(INVALID_COLOR_ERR, ephemeral=True)
            return
        team.color = color
        # Update role color if exists
        if team.role_id:
            role = interaction.guild.get_role(team.role_id)
            if role:
                try:
                    await role.edit(color=discord.Color(int(team.color, 16)))
                except (discord.Forbidden, discord.HTTPException) as e:
                    embeds.append(
                        discord.Embed(
                            title=ROLE_UPDATE_FAILED_TITLE,
                            description=ROLE_UPDATE_FAILED_DESC.format(e),
                            color=discord.Color.red()
                        )
                    )

    if owner is not None:
        if owner.bot:
            await interaction.response.send_message(CANNOT_SET_BOT_OWNER_ERR, ephemeral=True)
            return
        # Check if owner is a member of the team
        owner_is_member = any(member.id == owner.id for member in team.members)
        if not owner_is_member:
            await interaction.response.send_message(OWNER_NOT_MEMBER_ERR, ephemeral=True)
            return
        team.owner_id = owner.id

    if auto_accept is not None:
        team.auto_accept = auto_accept

    if reason is not None:
        team.reason = reason.strip()

    if link_role is not None:
        if team.role_id is not None:
            await interaction.response.send_message(ROLE_UPDATE_WITH_EXISTING_ERR, ephemeral=True)
            return
        team.role_id = link_role.id
        for team_member in team.members:
            member = interaction.guild.get_member(team_member.id)
            if member:
                try:
                    await member.add_roles(link_role)
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

    await update_team(interaction.guild.id, team)

    embed = discord.Embed(
        title=TEAM_UPDATED_TITLE,
        description=TEAM_UPDATED_DESC.format(team.name, team.tag),
        color=discord.Color.green()
    )
    embed.add_field(name=TEAM_UPDATED_FIELD_OWNER, value=FORMAT_USER_MENTION.format(
        team.owner_id), inline=True)
    embed.add_field(
        name=TEAM_UPDATED_FIELD_ROLE, value=FORMAT_ROLE_MENTION.format(team.role_id) if team.role_id else ROLE_NO_ROLE, inline=True)
    embed.add_field(name=TEAM_UPDATED_FIELD_TEAM_COLOR, value=FORMAT_TEAM_COLOR_DISPLAY.format(
        team.color), inline=True)
    embed.add_field(name=TEAM_UPDATED_FIELD_AUTO_ACCEPT,
                    value=format_bool_yes_no(team.auto_accept), inline=True)
    embeds.append(embed)

    await interaction.response.send_message(embeds=embeds, silent=True)


@group.command(name=UPDATE_TEAM_NAME_CMD, description=UPDATE_TEAM_NAME_CMD_DESC)
async def update_team_name(interaction: discord.Interaction, name: str) -> None:
    await update_team_common(interaction, name=name)


@group.command(name=UPDATE_TEAM_TAG_CMD, description=UPDATE_TEAM_TAG_CMD_DESC)
async def update_team_tag(interaction: discord.Interaction, tag: str) -> None:
    await update_team_common(interaction, tag=tag)


@group.command(name=UPDATE_TEAM_COLOR_CMD, description=UPDATE_TEAM_COLOR_CMD_DESC)
async def update_team_color(interaction: discord.Interaction, color: str) -> None:
    await update_team_common(interaction, color=color)


@group.command(name=UPDATE_TEAM_OWNER_CMD, description=UPDATE_TEAM_OWNER_CMD_DESC)
async def update_team_owner(interaction: discord.Interaction, owner: Member) -> None:
    await update_team_common(interaction, owner=owner)


@group.command(name=UPDATE_TEAM_AUTO_ACCEPT_CMD, description=UPDATE_TEAM_AUTO_ACCEPT_CMD_DESC)
async def update_team_auto_accept(interaction: discord.Interaction, auto_accept: bool) -> None:
    await update_team_common(interaction, auto_accept=auto_accept)


@group.command(name=UPDATE_TEAM_REASON_CMD, description=UPDATE_TEAM_REASON_CMD_DESC)
async def update_team_reason_placeholder(interaction: discord.Interaction, reason: str) -> None:
    await update_team_common(interaction, reason=reason)


@group.command(name=UPDATE_TEAM_ROLE_CMD, description=UPDATE_TEAM_ROLE_CMD_DESC)
async def update_team_role(interaction: discord.Interaction, role: Role) -> None:
    await update_team_common(interaction, link_role=role)
