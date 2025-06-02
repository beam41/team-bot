import discord
from discord import Member, Role, User, app_commands, ui
import re
import os
from dotenv import load_dotenv

from db import Team, add_team, get_team, load_team, remove_team, update_team

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

TEAM_THREAD_PARENT_ID = os.getenv('TEAM_THREAD_PARENT_ID')
if not TEAM_THREAD_PARENT_ID or not TEAM_THREAD_PARENT_ID.isdigit():
    raise ValueError(
        "TEAM_THREAD_PARENT_ID must be set and must be a valid integer.")
TEAM_THREAD_PARENT_ID = int(TEAM_THREAD_PARENT_ID)


class JoinRequestButtons(discord.ui.View):
    def __init__(self, team_id: int, user: User | Member, name: str, reason: str, ):
        super().__init__(timeout=None)
        self.team_id = team_id
        self.user = user
        self.name = name
        self.reason = reason

    @ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def green_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a guild.", ephemeral=True)
            return

        team = await get_team(interaction.guild.id, self.team_id)

        if not team:
            await interaction.response.send_message("No team registered in this thread.", ephemeral=True)
            return

        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("This command can only be used by members of the guild.", ephemeral=True)
            return

        if team.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You must be the team owner or an administrator to accept a join request.", ephemeral=True)
            return

        embeds = []

        # Add user to the team

        if (self.user.id in team.member):
            await interaction.response.send_message("User is already a member of this team.", ephemeral=True)
            await interaction.response.edit_message(view=None)
            return
        
        team.member.append(self.user.id)
        await update_team(interaction.guild.id, team)

        if team.role_id:
            role = interaction.guild.get_role(team.role_id)
            if role:
                try:
                    if isinstance(self.user, discord.Member):
                        await self.user.add_roles(role)
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

        members = "\n".join(
            [f"<@{member}>" for member in team.member])
        embed = discord.Embed(
            title="Team Joined",
            description=f"{self.user.mention} (IGN: {self.name}) have successfully join the team **{team.name}** **[{team.tag}]**, welcome to the team!.",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Reason", value=self.reason, inline=False)
        embed.add_field(name="Members", value=members, inline=False)
        embeds.append(embed)
        await interaction.response.edit_message(view=None)
        await interaction.followup.send(embeds=embeds)

    @ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def red_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a guild.", ephemeral=True)
            return

        team = await get_team(interaction.guild.id, self.team_id)

        if not team:
            await interaction.response.send_message("No team registered in this thread.", ephemeral=True)
            return

        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("This command can only be used by members of the guild.", ephemeral=True)
            return
        if team.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You must be the team owner or an administrator to reject a join request.", ephemeral=True)
            return
        embed = discord.Embed(
            title="Join Request Rejected",
            description="This join request has been rejected.",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)


class JoinRequestModal(ui.Modal, title='Join request question'):
    name = ui.TextInput(label='In game name',
                        style=discord.TextStyle.short, max_length=12)
    reason = ui.TextInput(
        label='Reason', style=discord.TextStyle.paragraph, max_length=200)

    def __init__(self, team: Team):
        self.reason.placeholder = f"{team.reason}{' (optional)' if team.auto_accept else ''}"
        self.reason.required = not team.auto_accept
        self.team_id = team.thread_id
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a guild.", ephemeral=True)
            return
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("This command can only be used by members of the guild.", ephemeral=True)
            return

        team = await get_team(interaction.guild.id, self.team_id)
        if not team:
            await interaction.response.send_message("No team registered in this thread.", ephemeral=True)
            return

        if team.auto_accept:
            embeds = []

            if interaction.user.id in team.member:
                await interaction.response.send_message("You are already a member of this team.", ephemeral=True)
                return

            # Add user to the team
            team.member.append(interaction.user.id)
            await update_team(interaction.guild.id, team)

            if team.role_id:
                role = interaction.guild.get_role(team.role_id)
                if role:
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

            members = "\n".join(
                [f"<@{member}>" for member in team.member])
            embed = discord.Embed(
                title="Team Joined",
                description=f"{interaction.user.mention} (IGN: {self.name.value}) have successfully join the team **{team.name}** **[{team.tag}]**, welcome to the team!.",
                color=discord.Color.green()
            )
            if self.reason.value:
                embed.add_field(
                    name="Reason", value=self.reason.value, inline=False)
            embed.add_field(name="Members", value=members, inline=False)
            embeds.append(embed)
            await interaction.response.send_message(embeds=embeds, silent=True)
            return

        button = JoinRequestButtons(
            team_id=team.thread_id, user=interaction.user, name=self.name.value, reason=self.reason.value)
        # If not auto accept, send join request
        embed = discord.Embed(
            title="Join Request",
            description=f"{interaction.user.mention} (IGN: {self.name.value}) has requested to join the team **{team.name}** **[{team.tag}]**.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Reason", value=self.reason.value, inline=False)
        embed.set_footer(
            text="Note: only the team owner can accept or reject this request.")
        await interaction.response.send_message(embed=embed, view=button, silent=True)


@tree.command(name="register_team", description="Register a team, use this under your team threads")
@app_commands.describe(
    name="Team name",
    tag="Team tag",
    team_color="Team official color (used in role)",
    auto_accept="Auto accept team members, aka FFA team",
    make_role="Make new role for the team (If your team already have role ask admin to link role to the team)",
    reason_placeholder="Placeholder for the reason input, this will be used on join request pop up"
)
async def register_team(interaction: discord.Interaction, name: str, tag: str, team_color: str, auto_accept: bool, make_role: bool, reason_placeholder: str):
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
    if make_role:
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

        if (role is not None):
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
        role.mention if role else "No role created") if make_role else "No role created", inline=True)
    embed.add_field(name="Team Color", value=f"#{team_color}", inline=True)
    embed.add_field(name="Auto Accept",
                    value="Yes" if auto_accept else "No", inline=True)
    embeds.append(embed)

    await interaction.response.send_message(embeds=embeds, silent=True)


@tree.command(name="unregister_team", description="Unregister a team, warn: this will delete the teams data and role if exists!")
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


@tree.command(name="team_details", description="View details of a team registered in this thread")
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

    members = "\n".join(
        [f"<@{member}>" for member in team.member])

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

group = app_commands.Group(name="update_team", description="Update a team")


async def update_team_common(interaction: discord.Interaction, *, name: str | None = None, tag: str | None = None, color: str | None = None, owner: User | None = None, auto_accept: bool | None = None, reason: str | None = None, role: Role | None = None) -> None:
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

    if role is not None:
        if team.role_id is not None:
            await interaction.response.send_message("You cannot update the role if the team already has a role assigned, update tag and color instead.", ephemeral=True)
            return
        team.role_id = role.id
        for member_id in team.member:
            member = interaction.guild.get_member(member_id)
            if member:
                try:
                    await member.add_roles(role)
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
    await update_team_common(interaction, role=role)

tree.add_command(group)


@tree.command(name="join_team", description="Join a team registered in this thread, join request will be posted if team is not auto accept")
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


@tree.command(name="leave_team", description="Leave a team registered in this thread, this will not notify anyone don't worry")
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


@tree.command(name="add_team_member", description="Add a member to team registered in this thread")
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


@tree.command(name="remove_team_member", description="Remove a member from team registered in this thread")
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


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    # Sync commands to the specific guild
    synced = await tree.sync()
    print(f'Synced {len(synced)} commands')

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN must be set in the environment variables.")
client.run(DISCORD_TOKEN)
