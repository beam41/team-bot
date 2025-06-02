from constants import TEAM_THREAD_PARENT_ID
from commands.ui.join_request import JoinRequestModal
from db import get_team, update_team
import discord
from discord import Member, User, app_commands


@app_commands.command(name="join_team", description="Join a team registered in this thread, join request will be posted if team is not auto accept")
async def join_team(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a guild.", ephemeral=True)
        return

    if not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message("This command can only be used by members of the guild.", ephemeral=True)
        return

    if not interaction.channel or interaction.channel.type != discord.ChannelType.public_thread or (interaction.channel.parent_id != TEAM_THREAD_PARENT_ID):
        await interaction.response.send_message("This command can only be used in team threads.", ephemeral=True)
        return

    team = await get_team(interaction.guild.id, interaction.channel.id)
    if not team:
        await interaction.response.send_message("No team registered in this thread.", ephemeral=True)
        return

    if interaction.user.id in team.member:
        await interaction.response.send_message("You are already a member of this team.", ephemeral=True)
        return

    # show for user to join team
    modal = JoinRequestModal(team)
    await interaction.response.send_modal(modal)


@app_commands.command(name="leave_team", description="Leave a team registered in this thread, this will not notify anyone don't worry")
async def leave_team(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a guild.", ephemeral=True)
        return

    if not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message("This command can only be used by members of the guild.", ephemeral=True)
        return

    if not interaction.channel or interaction.channel.type != discord.ChannelType.public_thread or (interaction.channel.parent_id != TEAM_THREAD_PARENT_ID):
        await interaction.response.send_message("This command can only be used in team threads.", ephemeral=True)
        return

    team = await get_team(interaction.guild.id, interaction.channel.id)
    if not team:
        await interaction.response.send_message("No team registered in this thread.", ephemeral=True)
        return

    if interaction.user.id not in team.member:
        await interaction.response.send_message("You are not a member of this team.", ephemeral=True)
        return

    if team.owner_id == interaction.user.id:
        await interaction.response.send_message("You cannot leave the team as the owner. Please transfer ownership or unregister the team.", ephemeral=True)
        return

    team.member.remove(interaction.user.id)
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
                        title="Role Removal Failed",
                        description="I do not have permission to unassign roles in this guild.",
                        color=discord.Color.red()
                    )
                )
            except discord.HTTPException as e:
                embeds.append(
                    discord.Embed(
                        title="Role Removal Failed",
                        description=f"Failed to unassign role: {e}",
                        color=discord.Color.red()
                    )
                )

    embed = discord.Embed(
        title="Team left",
        description=f"You have successfully leave the team **{team.name}** **[{team.tag}]**.",
        color=discord.Color.green()
    )
    embeds.append(embed)
    await interaction.response.send_message(embeds=embeds, silent=True, ephemeral=True)


@app_commands.command(name="add_team_member", description="Add a member to team registered in this thread")
async def add_team_member(interaction: discord.Interaction, new_member: User) -> None:
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a guild.", ephemeral=True)
        return

    if not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message("This command can only be used by members of the guild.", ephemeral=True)
        return

    if not interaction.channel or interaction.channel.type != discord.ChannelType.public_thread or (interaction.channel.parent_id != TEAM_THREAD_PARENT_ID):
        await interaction.response.send_message("This command can only be used in team threads.", ephemeral=True)
        return

    team = await get_team(interaction.guild.id, interaction.channel.id)
    if not team:
        await interaction.response.send_message("No team registered in this thread.", ephemeral=True)
        return

    if team.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You must be the team owner or an administrator to add members.", ephemeral=True)
        return

    if new_member.bot:
        await interaction.response.send_message("You cannot add a bot as a team member.", ephemeral=True)
        return

    if new_member.id in team.member:
        await interaction.response.send_message("User is already a member of this team.", ephemeral=True)
        return

    # Add user to the team
    team.member.append(new_member.id)
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
                        title="Role Assignment Failed",
                        description="I do not have permission to assign roles in this guild.",
                        color=discord.Color.red()
                    )
                )
            except discord.HTTPException as e:
                embeds.append(
                    discord.Embed(
                        title="Role Assignment Failed",
                        description=f"Failed to assign role: {e}",
                        color=discord.Color.red()
                    )
                )

    members = "\n".join([f"<@{member}>" for member in team.member])
    embed = discord.Embed(
        title="Team Member Added",
        description=f"<@{new_member.id}> has been added to team **{team.name}** **[{team.tag}]**.",
        color=discord.Color.green()
    )
    embed.add_field(name="Members", value=members, inline=False)
    embeds.append(embed)
    await interaction.response.send_message(embeds=embeds, silent=True)


@app_commands.command(name="remove_team_member", description="Remove a member from team registered in this thread")
async def remove_team_member(interaction: discord.Interaction, member: User) -> None:
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a guild.", ephemeral=True)
        return

    if not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message("This command can only be used by members of the guild.", ephemeral=True)
        return

    if not interaction.channel or interaction.channel.type != discord.ChannelType.public_thread or (interaction.channel.parent_id != TEAM_THREAD_PARENT_ID):
        await interaction.response.send_message("This command can only be used in team threads.", ephemeral=True)
        return

    team = await get_team(interaction.guild.id, interaction.channel.id)
    if not team:
        await interaction.response.send_message("No team registered in this thread.", ephemeral=True)
        return

    if team.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You must be the team owner or an administrator to remove members.", ephemeral=True)
        return

    if member.id == team.owner_id:
        await interaction.response.send_message("You cannot remove the team owner.", ephemeral=True)
        return

    if member.id not in team.member:
        await interaction.response.send_message("User is not a member of this team.", ephemeral=True)
        return

    team.member.remove(member.id)
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
                        title="Role Removal Failed",
                        description="I do not have permission to unassign roles in this guild.",
                        color=discord.Color.red()
                    )
                )
            except discord.HTTPException as e:
                embeds.append(
                    discord.Embed(
                        title="Role Removal Failed",
                        description=f"Failed to unassign role: {e}",
                        color=discord.Color.red()
                    )
                )

    members = "\n".join([f"<@{m}>" for m in team.member])
    embed = discord.Embed(
        title="Team Member Removed",
        description=f"<@{member.id}> has been removed from team **{team.name}** **[{team.tag}]**.",
        color=discord.Color.green()
    )
    embed.add_field(name="Members", value=members, inline=False)
    embeds.append(embed)
    await interaction.response.send_message(embeds=embeds, silent=True, ephemeral=True)
