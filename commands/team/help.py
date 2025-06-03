from discord import Embed, Interaction, app_commands
from strings import *
import discord
from typing import Dict, List, Optional, Tuple

# Define function to show specific command help


async def show_specific_command_help(interaction: Interaction, command_name: str, command_details: Dict[str, Tuple[str, str, str, str]]):
    """Show detailed help for a specific command"""
    # Clean up command name for matching (remove leading slash, etc.)
    command_name = command_name.lower().strip().lstrip('/')

    # Find the command in our details dictionary
    matching_command = None
    for cmd, details in command_details.items():
        if cmd.lower() == command_name or command_name in cmd.lower():
            matching_command = (cmd, details)
            break

    if not matching_command:
        # Didn't find an exact match, try partial matching
        for cmd, details in command_details.items():
            if command_name in cmd.lower():
                matching_command = (cmd, details)
                break

    if not matching_command:
        embed = Embed(
            title="Command Not Found",
            description=f"No command found matching '{command_name}'.\nUse `/help` without parameters to see all available commands.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Unpack the matched command details
    cmd, (desc, usage, category, example) = matching_command

    embed = Embed(
        title=f"Help: /{cmd}",
        description=desc,
        color=discord.Color.blue()
    )

    embed.add_field(name="Usage", value=f"```\n{usage}\n```", inline=False)
    embed.add_field(name="Category", value=category.capitalize(), inline=True)
    embed.add_field(name="Example", value=f"```\n{example}\n```", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@app_commands.command(name="team_help", description="Display help information about all team bot commands")
@app_commands.describe(command="Specific command to get detailed help for")
async def help_command(interaction: Interaction, command: Optional[str] = None):
    """Display help information about all team bot commands"""
    if not interaction.guild:
        await interaction.response.send_message(GUILD_ONLY_ERR, ephemeral=True)
        return

    # Command categories with their descriptions
    command_categories = {
        "team": "Team registration and management",
        "member": "Team membership commands",
        "position": "Team position management"
        # Command details dictionary with format: {'command_name': ('description', 'usage', 'category', 'examples')}
    }
    command_details = {
        # Team management commands
        f"{TEAM_CMD_GROUP} {REGISTER_TEAM_CMD}": (
            REGISTER_TEAM_CMD_DESC,
            f"/{TEAM_CMD_GROUP} {REGISTER_TEAM_CMD} name:<name> tag:<tag> team_color:<color> auto_accept:<bool> reason_placeholder:<text> [positions:<positions>] [skip_make_role:<bool>]",
            "team",
            f"/{TEAM_CMD_GROUP} {REGISTER_TEAM_CMD} name:RedTeam tag:RED team_color:red auto_accept:false reason_placeholder:\"Why do you want to join?\" positions:\"Driver,Support,Coach\""
        ),
        f"{TEAM_CMD_GROUP} {UNREGISTER_TEAM_CMD}": (
            UNREGISTER_TEAM_CMD_DESC,
            f"/{TEAM_CMD_GROUP} {UNREGISTER_TEAM_CMD}",
            "team",
            f"/{TEAM_CMD_GROUP} {UNREGISTER_TEAM_CMD}"
        ),
        f"{TEAM_CMD_GROUP} {TEAM_DETAILS_CMD}": (
            TEAM_DETAILS_CMD_DESC,
            f"/{TEAM_CMD_GROUP} {TEAM_DETAILS_CMD}",
            "team",
            f"/{TEAM_CMD_GROUP} {TEAM_DETAILS_CMD}"
        ),

        # Team membership commands
        f"{JOIN_TEAM_CMD}": (
            JOIN_TEAM_CMD_DESC,
            f"/{JOIN_TEAM_CMD}",
            "member",
            f"/{JOIN_TEAM_CMD}"
        ),
        f"{LEAVE_TEAM_CMD}": (
            LEAVE_TEAM_CMD_DESC,
            f"/{LEAVE_TEAM_CMD}",
            "member",
            f"/{LEAVE_TEAM_CMD}"
        ),        # Team member management commands
        f"{TEAM_MEMBER_CMD_GROUP} {ADD_TEAM_MEMBER_CMD}": (
            ADD_TEAM_MEMBER_CMD_DESC,
            f"/{TEAM_MEMBER_CMD_GROUP} {ADD_TEAM_MEMBER_CMD} new_member:<@member> number:<int> [position:<position>]",
            "member",
            f"/{TEAM_MEMBER_CMD_GROUP} {ADD_TEAM_MEMBER_CMD} new_member:@username number:42 position:Driver"
        ),
        f"{TEAM_MEMBER_CMD_GROUP} {REMOVE_TEAM_MEMBER_CMD}": (
            REMOVE_TEAM_MEMBER_CMD_DESC,
            f"/{TEAM_MEMBER_CMD_GROUP} {REMOVE_TEAM_MEMBER_CMD} member:<@member>",
            "member",
            f"/{TEAM_MEMBER_CMD_GROUP} {REMOVE_TEAM_MEMBER_CMD} member:@username"
        ),

        # Member update commands
        f"{TEAM_MEMBER_CMD_GROUP} {UPDATE_MEMBER_INFO_CMD_GROUP} {CHANGE_PLAYER_NUMBER_CMD}": (
            CHANGE_PLAYER_NUMBER_CMD_DESC,
            f"/{TEAM_MEMBER_CMD_GROUP} {UPDATE_MEMBER_INFO_CMD_GROUP} {CHANGE_PLAYER_NUMBER_CMD} new_number:<int> [member:<@member>]",
            "member",
            f"/{TEAM_MEMBER_CMD_GROUP} {UPDATE_MEMBER_INFO_CMD_GROUP} {CHANGE_PLAYER_NUMBER_CMD} new_number:7 member:@username"
        ),
        f"{TEAM_MEMBER_CMD_GROUP} {UPDATE_MEMBER_INFO_CMD_GROUP} {CHANGE_POSITION_CMD}": (
            CHANGE_POSITION_CMD_DESC,
            f"/{TEAM_MEMBER_CMD_GROUP} {UPDATE_MEMBER_INFO_CMD_GROUP} {CHANGE_POSITION_CMD} position:<position> [member:<@member>]",
            "member",
            f"/{TEAM_MEMBER_CMD_GROUP} {UPDATE_MEMBER_INFO_CMD_GROUP} {CHANGE_POSITION_CMD} position:Driver member:@username"
        ),

        # Team update commands
        f"{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_NAME_CMD}": (
            UPDATE_TEAM_NAME_CMD_DESC,
            f"/{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_NAME_CMD} name:<new_name>",
            "team",
            f"/{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_NAME_CMD} name:\"Blue Dragons\""
        ),
        f"{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_TAG_CMD}": (
            UPDATE_TEAM_TAG_CMD_DESC,
            f"/{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_TAG_CMD} tag:<new_tag>",
            "team",
            f"/{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_TAG_CMD} tag:BLD"
        ),
        f"{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_COLOR_CMD}": (
            UPDATE_TEAM_COLOR_CMD_DESC,
            f"/{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_COLOR_CMD} color:<new_color>",
            "team",
            f"/{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_COLOR_CMD} color:blue"
        ),
        f"{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_OWNER_CMD}": (
            UPDATE_TEAM_OWNER_CMD_DESC,
            f"/{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_OWNER_CMD} owner:<@new_owner>",
            "team",
            f"/{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_OWNER_CMD} owner:@username"
        ),
        f"{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_AUTO_ACCEPT_CMD}": (
            UPDATE_TEAM_AUTO_ACCEPT_CMD_DESC,
            f"/{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_AUTO_ACCEPT_CMD} auto_accept:<bool>",
            "team",
            f"/{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_AUTO_ACCEPT_CMD} auto_accept:true"
        ),
        f"{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_REASON_CMD}": (
            UPDATE_TEAM_REASON_CMD_DESC,
            f"/{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_REASON_CMD} reason_placeholder:<text>",
            "team",
            f"/{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_REASON_CMD} reason_placeholder:\"Tell us about your experience\""
        ),
        f"{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_ROLE_CMD}": (
            UPDATE_TEAM_ROLE_CMD_DESC,
            f"/{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_ROLE_CMD} link_role:<@role>",
            "team",
            f"/{UPDATE_TEAM_CMD_GROUP} {UPDATE_TEAM_ROLE_CMD} link_role:@TeamRole"
        ),

        # Team position management commands
        f"{UPDATE_TEAM_CMD_GROUP} position {ADD_POSITION_CMD}": (
            ADD_POSITION_CMD_DESC,
            f"/{UPDATE_TEAM_CMD_GROUP} position {ADD_POSITION_CMD} position:<name>",
            "position",
            f"/{UPDATE_TEAM_CMD_GROUP} position {ADD_POSITION_CMD} position:\"Team Coach\""
        ),
        f"{UPDATE_TEAM_CMD_GROUP} position {EDIT_POSITION_CMD}": (
            EDIT_POSITION_CMD_DESC,
            f"/{UPDATE_TEAM_CMD_GROUP} position {EDIT_POSITION_CMD} position:<current_name> new_position:<new_name>",
            "position",
            f"/{UPDATE_TEAM_CMD_GROUP} position {EDIT_POSITION_CMD} position:Driver new_position:\"Lead Driver\""
        ),
        f"{UPDATE_TEAM_CMD_GROUP} position {DELETE_POSITION_CMD}": (
            DELETE_POSITION_CMD_DESC,
            f"/{UPDATE_TEAM_CMD_GROUP} position {DELETE_POSITION_CMD} position:<name>",
            "position",
            f"/{UPDATE_TEAM_CMD_GROUP} position {DELETE_POSITION_CMD} position:\"Substitute\""
        )
    }

    # If specific command help is requested
    if command:
        await show_specific_command_help(interaction, command, command_details)
        return

    help_embeds = []

    # Create category embeds
    for category, desc in command_categories.items():
        embed = Embed(
            title=f"{category.capitalize()} Commands",
            description=desc,
            color=discord.Color.blue()
        )

        # Add all commands for this category
        for cmd_name, (cmd_desc, usage, cmd_category, _) in command_details.items():
            if cmd_category == category:
                embed.add_field(
                    name=f"/{cmd_name}",
                    value=f"{cmd_desc}\n"
                    f"Usage: `{usage}`",
                    inline=False
                )

        if embed.fields:  # Only add if there are commands in this category
            help_embeds.append(embed)

    # General notes embed
    notes_embed = Embed(
        title="Important Notes",
        description="General information about using the Team Bot commands",
        color=discord.Color.dark_gray()
    )
    notes_embed.add_field(
        name="Thread Contexts",
        value="Team commands must be used in teams threads.",
        inline=False
    )
    notes_embed.add_field(
        name="Specific Command Help",
        value="To get detailed help for a specific command, use: `/help command:<command_name>`\n"
              "For example: `/help command:team register` or `/help command:join_team`",
        inline=False
    )
    help_embeds.append(notes_embed)

    # Send all embeds
    await interaction.response.send_message(embeds=help_embeds, ephemeral=True)
