from env import TEAM_THREAD_PARENT_ID
from db import get_team, update_team, TeamMember
from utils import format_team_members
import discord
from discord import Member, app_commands
from typing import Optional
from strings import *

# Create the command group
group = app_commands.Group(name=TEAM_MEMBER_CMD_GROUP,
                           description=TEAM_MEMBER_CMD_GROUP_DESC)


@group.command(name='add', description=ADD_TEAM_MEMBER_CMD_DESC)
async def add_team_member(interaction: discord.Interaction, new_member: Member, number: int, position: Optional[str]) -> None:
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
        await interaction.response.send_message(TEAM_OWNER_OR_ADMIN_ADD_ERR, ephemeral=True)
        return

    if new_member.bot:
        await interaction.response.send_message(CANNOT_ADD_BOT_ERR, ephemeral=True)
        return

    # Validate player number
    if number < 0 or number > 99:
        await interaction.response.send_message(PLAYER_NUMBER_RANGE_ERR, ephemeral=True)
        return

    # Check if user is already a member
    if any(member.id == new_member.id for member in team.members):
        await interaction.response.send_message(USER_ALREADY_MEMBER_ERR, ephemeral=True)
        return

    # Create the team member object
    team_member = TeamMember(id=new_member.id, number=number)

    # If position is specified, assign it to the member
    position_name = None
    if position:
        position = position.strip()
        position_obj = None
        for pos in team.positions:
            if pos.name == position:
                position_obj = pos
                break

        if position_obj:
            team_member.pos_id = position_obj.id
            position_name = position_obj.name
        else:
            await interaction.response.send_message(POSITION_NOT_FOUND_ERR, ephemeral=True)
            return

    team.members.append(team_member)
    await update_team(interaction.guild.id, team)

    embeds = []

    if team.role_id:
        role = interaction.guild.get_role(team.role_id)
        if role and isinstance(new_member, discord.Member):
            try:
                await new_member.add_roles(role)
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

    members = format_team_members(team.members, team.positions)
    embed = discord.Embed(
        title=TEAM_MEMBER_ADDED_TITLE,
        description=TEAM_MEMBER_ADDED_DESC.format(
            new_member.id, team.name, team.tag, number, f" {AS} **{position_name}**" if position_name else ""),
        color=discord.Color.green()
    )
    embed.add_field(name=TEAM_MEMBER_ADDED_FIELD_CURRENT_MEMBERS,
                    value=members, inline=False)
    embeds.append(embed)
    await interaction.response.send_message(embeds=embeds, silent=True)


@group.command(name='remove', description=REMOVE_TEAM_MEMBER_CMD_DESC)
async def remove_team_member(interaction: discord.Interaction, member: Member) -> None:
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
        await interaction.response.send_message(TEAM_OWNER_OR_ADMIN_REMOVE_ERR, ephemeral=True)
        return

    if member.id == team.owner_id:
        await interaction.response.send_message(CANNOT_REMOVE_OWNER_ERR, ephemeral=True)
        return

    if not any(m.id == member.id for m in team.members):
        await interaction.response.send_message(USER_NOT_MEMBER_ERR, ephemeral=True)
        return

    # Remove the member from the team
    team.members = [m for m in team.members if m.id != member.id]
    await update_team(interaction.guild.id, team)

    embeds = []

    if team.role_id:
        role = interaction.guild.get_role(team.role_id)
        if role and isinstance(member, discord.Member):
            try:
                await member.remove_roles(role)
            except discord.Forbidden:
                embeds.append(
                    discord.Embed(
                        title=ROLE_REMOVAL_FAILED_TITLE,
                        description=ROLE_REMOVAL_FAILED_DESC_PERMISSION,
                        color=discord.Color.red()
                    )
                )
            except discord.HTTPException as e:
                embeds.append(
                    discord.Embed(
                        title=ROLE_REMOVAL_FAILED_TITLE,
                        description=ROLE_REMOVAL_FAILED_DESC_FAILED.format(e),
                        color=discord.Color.red()
                    )
                )

    members = format_team_members(team.members, team.positions)
    embed = discord.Embed(
        title=TEAM_MEMBER_REMOVED_TITLE,
        description=TEAM_MEMBER_REMOVED_DESC.format(
            member.id, team.name, team.tag),
        color=discord.Color.green()
    )
    embed.add_field(name=TEAM_MEMBER_REMOVED_FIELD_CURRENT_MEMBERS,
                    value=members, inline=False)
    embeds.append(embed)
    await interaction.response.send_message(embeds=embeds, silent=True, ephemeral=True)
