from db import Team, get_team, update_team
import discord
from discord import Member, User, ui


class JoinRequestButtons(discord.ui.View):
    def __init__(self, team_id: int, user: User | Member, name: str, reason: str):
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
        if self.user.id in team.member:
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

        members = "\n".join([f"<@{member}>" for member in team.member])
        embed = discord.Embed(
            title="Team Joined",
            description=f"{self.user.mention} (IGN: {self.name}) have successfully join the team **{team.name}** **[{team.tag}]**, welcome to the team!.",
            color=discord.Color.green()
        )
        embed.add_field(name="Reason", value=self.reason, inline=False)
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

            members = "\n".join([f"<@{member}>" for member in team.member])
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
