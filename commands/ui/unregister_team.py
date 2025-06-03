import discord
from discord import ui
from db import get_team, remove_team
from env import TEAM_THREAD_PARENT_ID
from strings import *


class UnregisterTeamConfirmButton(discord.ui.View):
    @ui.button(label=BOOL_YES, style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild:
            await interaction.followup.send(GUILD_ONLY_ERR, ephemeral=True)
            return

        if not isinstance(interaction.user, discord.Member):
            await interaction.followup.send(MEMBERS_ONLY_ERR, ephemeral=True)
            return

        if not interaction.channel or interaction.channel.type != discord.ChannelType.public_thread or (interaction.channel.parent_id != TEAM_THREAD_PARENT_ID):
            await interaction.followup.send(TEAM_THREADS_ONLY_ERR, ephemeral=True)
            return

        team = await get_team(interaction.guild.id, interaction.channel.id)
        if not team:
            await interaction.followup.send(NO_TEAM_REGISTERED_ERR, ephemeral=True)
            return

        if team.owner_id != interaction.user.id and not interaction.user.guild_permissions.administrator:
            await interaction.followup.send(TEAM_OWNER_OR_ADMIN_ERR, ephemeral=True)
            return

        embeds = []

        # Try to delete the role if it exists
        if team.role_id:
            role = interaction.guild.get_role(team.role_id)
            if role:
                try:
                    await role.delete()
                except discord.Forbidden:
                    embeds.append(
                        discord.Embed(
                            title=ROLE_DELETION_FAILED_TITLE,
                            description=ROLE_DELETION_FAILED_DESC_PERMISSION,
                            color=discord.Color.red()
                        )
                    )
                except discord.HTTPException as e:
                    embeds.append(
                        discord.Embed(
                            title=ROLE_DELETION_FAILED_TITLE,
                            description=ROLE_DELETION_FAILED_DESC_FAILED.format(
                                e),
                            color=discord.Color.red()
                        )
                    )

        # Remove the team from the database
        await remove_team(interaction.guild.id, interaction.channel.id)

        embed = discord.Embed(
            title=TEAM_UNREGISTERED_TITLE,
            description=TEAM_UNREGISTERED_DESC.format(team.name, team.tag),
            color=discord.Color.green()
        )
        embeds.append(embed)
        await interaction.response.edit_message(embeds=embeds, view=None)

    @ui.button(label=BOOL_NO, style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=UNREGISTRATION_CANCELLED_TITLE,
            description=UNREGISTRATION_CANCELLED_DESC,
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=None)
