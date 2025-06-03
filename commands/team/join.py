from env import TEAM_THREAD_PARENT_ID
from commands.ui.join_request import JoinRequestModal
from db import get_team, update_team
import discord
from discord import app_commands
from strings import *


@app_commands.command(name=JOIN_TEAM_CMD, description=JOIN_TEAM_CMD_DESC)
async def join_team(interaction: discord.Interaction):
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

    if any(member.id == interaction.user.id for member in team.members):
        await interaction.response.send_message(ALREADY_TEAM_MEMBER_ERR, ephemeral=True)
        return

    # show for user to join team
    modal = JoinRequestModal(team)
    await interaction.response.send_modal(modal)


@app_commands.command(name=LEAVE_TEAM_CMD, description=LEAVE_TEAM_CMD_DESC)
async def leave_team(interaction: discord.Interaction):
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

    if not any(member.id == interaction.user.id for member in team.members):
        await interaction.response.send_message(NOT_TEAM_MEMBER_ERR, ephemeral=True)
        return

    if team.owner_id == interaction.user.id:
        await interaction.response.send_message(OWNER_CANNOT_LEAVE_ERR, ephemeral=True)
        return

    # Remove the member from the team
    team.members = [
        member for member in team.members if member.id != interaction.user.id]
    await update_team(interaction.guild.id, team)

    embeds = []

    if team.role_id:
        role = interaction.guild.get_role(team.role_id)
        if role:
            try:
                await interaction.user.remove_roles(role)
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

    embed = discord.Embed(
        title=TEAM_LEFT_TITLE,
        description=TEAM_LEFT_DESC.format(team.name, team.tag),
        color=discord.Color.green()
    )
    embeds.append(embed)
    await interaction.response.send_message(embeds=embeds, silent=True, ephemeral=True)
