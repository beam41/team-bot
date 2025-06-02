from constants import TEAM_THREAD_PARENT_ID
from db import get_team, load_team, update_team
import discord
from discord import Member, Role, User, app_commands
import re


group = app_commands.Group(name="update_team", description="Update a team")


async def update_team_common(interaction: discord.Interaction, *, name: str | None = None, tag: str | None = None, color: str | None = None, owner: User | None = None, auto_accept: bool | None = None, reason: str | None = None, link_role: Role | None = None) -> None:
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

    if link_role:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You must an administrator to update a team.", ephemeral=True)
            return
    else:
        if team.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You must be the team owner or an administrator to update a team.", ephemeral=True)
            return

    embeds = []

    if name is not None:
        name = name.strip()
        teams = await load_team(interaction.guild.id)
        for t in teams:
            if t.name == name:
                await interaction.response.send_message("Team is already registered with the same name.", ephemeral=True)
                return
        team.name = name

    if tag is not None:
        if not re.match(r'^[A-Z0-9]{2,6}$', tag):
            await interaction.response.send_message("Invalid team tag. Please provide a valid tag (2-6 uppercase letters or numbers).", ephemeral=True)
            return
        teams = await load_team(interaction.guild.id)
        for t in teams:
            if t.tag == tag:
                await interaction.response.send_message("Team is already registered with the same tag.", ephemeral=True)
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
                            title="Role Update Failed",
                            description=f"Failed to update role: {e}",
                            color=discord.Color.red()
                        )
                    )

    if color is not None:
        color = color.lstrip('#').upper()
        if not re.match(r'^[0-9A-F]{6}$', color):
            await interaction.response.send_message("Invalid team color. Please provide a valid hex color code (6 characters, e.g., 'FF5733').", ephemeral=True)
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
                            title="Role Update Failed",
                            description=f"Failed to update role: {e}",
                            color=discord.Color.red()
                        )
                    )

    if owner is not None:
        if owner.bot:
            await interaction.response.send_message("You cannot set a bot as the team owner.", ephemeral=True)
            return
        if owner.id not in team.member:
            await interaction.response.send_message("The specified user is not a member of the team.", ephemeral=True)
            return
        team.owner_id = owner.id

    if auto_accept is not None:
        team.auto_accept = auto_accept

    if reason is not None:
        team.reason = reason.strip()

    if link_role is not None:
        if team.role_id is not None:
            await interaction.response.send_message("You cannot update the role if the team already has a role assigned, update tag and color instead.", ephemeral=True)
            return
        team.role_id = link_role.id
        for member_id in team.member:
            member = interaction.guild.get_member(member_id)
            if member:
                try:
                    await member.add_roles(link_role)
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

    await update_team(interaction.guild.id, team)

    embed = discord.Embed(
        title="Team Updated",
        description=f"Team **{team.name}**  **[{team.tag}]** has been updated successfully.",
        color=discord.Color.blue()
    )
    embed.add_field(name="Owner", value=f"<@{team.owner_id}>", inline=True)
    embed.add_field(
        name="Role", value=f"<@&{team.role_id}>" if team.role_id else "No role", inline=True)
    embed.add_field(name="Team Color", value=f"#{team.color}", inline=True)
    embed.add_field(name="Auto Accept",
                    value="Yes" if team.auto_accept else "No", inline=True)
    embeds.append(embed)

    await interaction.response.send_message(embeds=embeds, silent=True)


@group.command(name="name", description="Update the team name")
async def update_team_name(interaction: discord.Interaction, name: str) -> None:
    await update_team_common(interaction, name=name)


@group.command(name="tag", description="Update the team tag")
async def update_team_tag(interaction: discord.Interaction, tag: str) -> None:
    await update_team_common(interaction, tag=tag)


@group.command(name="color", description="Update the team color")
async def update_team_color(interaction: discord.Interaction, color: str) -> None:
    await update_team_common(interaction, color=color)


@group.command(name="owner", description="Update the team owner")
async def update_team_owner(interaction: discord.Interaction, owner: User) -> None:
    await update_team_common(interaction, owner=owner)


@group.command(name="auto_accept", description="Update the team auto_accept")
async def update_team_auto_accept(interaction: discord.Interaction, auto_accept: bool) -> None:
    await update_team_common(interaction, auto_accept=auto_accept)


@group.command(name="reason_placeholder", description="Update the team join request reason placeholder")
async def update_team_reason_placeholder(interaction: discord.Interaction, reason: str) -> None:
    await update_team_common(interaction, reason=reason)


@group.command(name="role", description="Update the team role (only work when there is no role assigned)")
async def update_team_role(interaction: discord.Interaction, role: Role) -> None:
    await update_team_common(interaction, link_role=role)
