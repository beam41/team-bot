from cProfile import label
from turtle import position
from db import Team, TeamMember, get_team, update_team
from utils import format_team_members
import discord
from discord import Member, User, ui
from strings import *


class JoinRequestButtons(discord.ui.View):
    def __init__(self, team_id: int, user: User | Member, name: str, reason: str, number: int):
        super().__init__(timeout=None)
        self.team_id = team_id
        self.user = user
        self.name = name
        self.reason = reason
        self.number = number

    @ui.button(label=UI_BUTTON_ACCEPT, style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild:
            await interaction.followup.send(GUILD_ONLY_ERR, ephemeral=True)
            return

        team = await get_team(interaction.guild.id, self.team_id)

        if not team:
            await interaction.followup.send(NO_TEAM_REGISTERED_ERR, ephemeral=True)
            return

        if not isinstance(interaction.user, discord.Member):
            await interaction.followup.send(MEMBERS_ONLY_ERR, ephemeral=True)
            return

        if team.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
            await interaction.followup.send(TEAM_OWNER_OR_ADMIN_ACCEPT_ERR, ephemeral=True)
            return

        embeds = []

        # Check if user is already a member
        if any(member.id == self.user.id for member in team.members):
            await interaction.response.edit_message(view=None)
            await interaction.followup.send(USER_ALREADY_MEMBER_ERR, ephemeral=True)
            return

        # Add user to the team with their number
        new_member = TeamMember(id=self.user.id, number=self.number)
        team.members.append(new_member)
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
            title=TEAM_JOINED_TITLE,
            description=TEAM_JOINED_DESC.format(
                self.user.mention, self.name, team.name, team.tag, self.number),
            color=discord.Color.green()
        )
        embed.add_field(name=TEAM_JOINED_FIELD_REASON,
                        value=self.reason, inline=False)
        embed.add_field(name=TEAM_JOINED_FIELD_MEMBERS,
                        value=members, inline=False)
        embeds.append(embed)
        await interaction.response.edit_message(view=None)
        await interaction.followup.send(embeds=embeds, silent=True)

    @ui.button(label=UI_BUTTON_REJECT, style=discord.ButtonStyle.red)
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild:
            await interaction.response.send_message(GUILD_ONLY_ERR, ephemeral=True)
            return

        team = await get_team(interaction.guild.id, self.team_id)

        if not team:
            await interaction.response.send_message(NO_TEAM_REGISTERED_ERR, ephemeral=True)
            return

        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(MEMBERS_ONLY_ERR, ephemeral=True)
            return

        if team.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(TEAM_OWNER_OR_ADMIN_REJECT_ERR, ephemeral=True)
            return

        embed = discord.Embed(
            title=JOIN_REQUEST_REJECTED_TITLE,
            description=JOIN_REQUEST_REJECTED_DESC,
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)


class JoinRequestModal(ui.Modal, title=UI_MODAL_TITLE):
    name = ui.TextInput(label=UI_LABEL_IGN,
                        style=discord.TextStyle.short, max_length=12)
    number = ui.TextInput(label=UI_LABEL_PLAYER_NUMBER,
                          style=discord.TextStyle.short, max_length=2, min_length=1, placeholder=UI_PLACEHOLDER_PLAYER_NUMBER)
    reason = ui.TextInput(
        label=UI_LABEL_REASON, style=discord.TextStyle.paragraph, max_length=200)

    def __init__(self, team: Team):
        self.reason.placeholder = UI_PLACEHOLDER_REASON_OPTIONAL.format(
            team.reason) if team.auto_accept else team.reason
        self.reason.required = not team.auto_accept
        self.team_id = team.thread_id
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message(GUILD_ONLY_ERR, ephemeral=True)
            return
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(MEMBERS_ONLY_ERR, ephemeral=True)
            return

        # Validate player number
        try:
            player_number = int(self.number.value)
            if player_number < 0 or player_number > 99:
                await interaction.response.send_message(PLAYER_NUMBER_RANGE_ERR, ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message(PLAYER_NUMBER_INVALID_ERR, ephemeral=True)
            return

        team = await get_team(interaction.guild.id, self.team_id)
        if not team:
            await interaction.response.send_message(NO_TEAM_REGISTERED_ERR, ephemeral=True)
            return

        # Check if user is already a member
        if any(member.id == interaction.user.id for member in team.members):
            await interaction.response.send_message(ALREADY_TEAM_MEMBER_ERR, ephemeral=True)
            return

        if team.auto_accept:
            embeds = []

            # Add user to the team with their number
            new_member = TeamMember(
                id=interaction.user.id, number=player_number)
            team.members.append(new_member)
            await update_team(interaction.guild.id, team)

            if team.role_id:
                role = interaction.guild.get_role(team.role_id)
                if role:
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

            members = format_team_members(team.members, team.positions)
            embed = discord.Embed(
                title=TEAM_JOINED_TITLE,
                description=TEAM_JOINED_DESC.format(
                    interaction.user.mention, self.name.value, team.name, team.tag, player_number),
                color=discord.Color.green()
            )
            if self.reason.value:
                embed.add_field(
                    name=TEAM_JOINED_FIELD_REASON, value=self.reason.value, inline=False)
            embed.add_field(name=TEAM_JOINED_FIELD_MEMBERS,
                            value=members, inline=False)
            embeds.append(embed)
            await interaction.response.send_message(embeds=embeds, silent=True)
            return

        button = JoinRequestButtons(
            team_id=team.thread_id, user=interaction.user, name=self.name.value, reason=self.reason.value, number=player_number)
        # If not auto accept, send join request
        embed = discord.Embed(
            title=JOIN_REQUEST_TITLE,
            description=JOIN_REQUEST_DESC.format(
                interaction.user.mention, self.name.value, team.name, team.tag, player_number),
            color=discord.Color.blue()
        )
        embed.add_field(name=TEAM_JOINED_FIELD_REASON,
                        value=self.reason.value, inline=False)
        embed.set_footer(text=UI_NOTE_OWNER_ONLY)
        await interaction.response.send_message(embed=embed, view=button, silent=True)
