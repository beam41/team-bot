from constants import TEAM_THREAD_PARENT_ID
from db import Team, add_team, get_team, load_team, remove_team
import discord
from discord import app_commands
import re



@app_commands.command(name="register_team", description="Register a team, use this under your team threads")
@app_commands.describe(
    name="Team name",
    tag="Team tag",
    team_color="Team official color (used in role)",
    auto_accept="Auto accept team members, aka FFA team",
    reason_placeholder="Placeholder for the reason input, this will be used on join request pop up",
    skip_make_role="For legacy team, ask admin to link role to the team",
)
async def register_team(interaction: discord.Interaction, name: str, tag: str, team_color: str, auto_accept: bool, reason_placeholder: str, skip_make_role: bool = True):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a guild.", ephemeral=True)
        return

    if not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message("This command can only be used by members of the guild.", ephemeral=True)
        return

    if not interaction.channel or interaction.channel.type != discord.ChannelType.public_thread or (interaction.channel.parent_id != TEAM_THREAD_PARENT_ID):
        await interaction.response.send_message("This command can only be used in team threads.", ephemeral=True)
        return

    if interaction.channel.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You must be the thread owner or administrator to register a team.", ephemeral=True)
        return

    name = name.strip()
    # Remove leading '#' if present
    team_color = team_color.lstrip('#').upper()

    if not re.match(r'^[0-9A-F]{6}$', team_color):
        await interaction.response.send_message("Invalid team color. Please provide a valid hex color code (6 characters, e.g., 'FF5733').", ephemeral=True)
        return

    if not re.match(r'^[A-Z0-9]{2,6}$', tag):
        await interaction.response.send_message("Invalid team tag. Please provide a valid tag (2-6 uppercase letters or numbers).", ephemeral=True)
        return

    teams = await load_team(interaction.guild.id)
    # Check if a team with the same name or tag already exists
    for team in teams:
        if team.thread_id == interaction.channel.id:
            await interaction.response.send_message("Team is already registered in this thread.", ephemeral=True)
            return
        if team.name == name or team.tag == tag:
            await interaction.response.send_message("Team is already registered with the same name or tag.", ephemeral=True)
            return

    embeds = []
    role = None
    if not skip_make_role:
        # Create a new role with the specified color
        try:
            role = await interaction.guild.create_role(
                name=tag,
                color=discord.Color(int(team_color, 16)),
                mentionable=True,
            )
        except discord.Forbidden:
            embeds.append(
                discord.Embed(
                    title="Role Creation Failed",
                    description="I do not have permission to create roles in this guild, please ask admin to create manually.",
                    color=discord.Color.red()
                )
            )
        except discord.HTTPException as e:
            embeds.append(
                discord.Embed(
                    title="Role Creation Failed",
                    description=f"Failed to create role: {e}, please ask admin to create manually.",
                    color=discord.Color.red()
                )
            )

        if role is not None:
            try:
                await interaction.user.add_roles(role)
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

    await add_team(interaction.guild.id, Team(
        thread_id=interaction.channel.id,
        owner_id=interaction.user.id,
        role_id=role.id if role else None,
        name=name,
        tag=tag,
        color=team_color,
        auto_accept=auto_accept,
        member=[interaction.user.id],
        reason=reason_placeholder.strip(),
    ))

    embed = discord.Embed(
        title="Team Registered",
        description=f"Team **{name}** **[{tag}]** has been registered successfully.",
        color=discord.Color.green()
    )
    embed.add_field(name="Owner", value=interaction.user.mention, inline=True)
    embed.add_field(name="Role", value=(
        role.mention if role else "No role created") if not skip_make_role else "No role created", inline=True)
    embed.add_field(name="Team Color", value=f"#{team_color}", inline=True)
    embed.add_field(name="Auto Accept",
                    value="Yes" if auto_accept else "No", inline=True)
    embeds.append(embed)

    await interaction.response.send_message(embeds=embeds, silent=True)


@app_commands.command(name="unregister_team", description="Unregister a team, warn: this will delete the teams data and role if exists!")
async def unregister_team(interaction: discord.Interaction):
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
        await interaction.response.send_message("You must be the team owner or an administrator to unregister a team.", ephemeral=True)
        return

    embeds = []

    if team.role_id:
        role = interaction.guild.get_role(team.role_id)
        if role:
            try:
                await role.delete()
            except discord.Forbidden:
                embeds.append(
                    discord.Embed(
                        title="Role Deletion Failed",
                        description="I do not have permission to delete roles in this guild, please ask admin to delete manually.",
                        color=discord.Color.red()
                    )
                )
            except discord.HTTPException as e:
                embeds.append(
                    discord.Embed(
                        title="Role Deletion Failed",
                        description=f"Failed to delete role: {e}, please ask admin to delete manually.",
                        color=discord.Color.red()
                    )
                )

    await remove_team(interaction.guild.id, team.thread_id)

    embed = discord.Embed(
        title="Team Unregistered",
        description=f"Team **{team.name}** **[{team.tag}]** has been unregistered successfully.",
        color=discord.Color.red()
    )
    embeds.append(embed)
    await interaction.response.send_message(embeds=embeds, silent=True)


@app_commands.command(name="team_details", description="View details of a team registered in this thread")
async def team_details(interaction: discord.Interaction):
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

    members = "\n".join([f"<@{member}>" for member in team.member])

    embed = discord.Embed(
        title="Team Details",
        description=f"Team **{team.name}**  **[{team.tag}]**",
        color=discord.Color.blue()
    )
    embed.add_field(name="Owner", value=f"<@{team.owner_id}>", inline=True)
    embed.add_field(
        name="Role", value=f"<@&{team.role_id}>" if team.role_id else "No role", inline=True)
    embed.add_field(name="Team Color", value=f"#{team.color}", inline=True)
    embed.add_field(name="Auto Accept",
                    value="Yes" if team.auto_accept else "No", inline=True)
    embed.add_field(name="Members", value=members, inline=False)

    await interaction.response.send_message(embed=embed, silent=True, ephemeral=True)
