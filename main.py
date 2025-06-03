import discord
import os
from dotenv import load_dotenv
from strings import *

# Import all command modules from the organized structure
from commands import (
    team_group,
    join_team,
    leave_team,
    update_member_group,
    update_team_group
)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

# Register all commands
tree.add_command(join_team)
tree.add_command(leave_team)
tree.add_command(team_group)
tree.add_command(update_member_group)
tree.add_command(update_team_group)


@client.event
async def on_ready():
    print(FORMAT_LOGGED_IN.format(client.user))
    # Sync commands to the specific guild
    synced = await tree.sync()
    print(FORMAT_SYNCED_COMMANDS.format(len(synced)))


if __name__ == "__main__":
    DISCORD_TOKEN = os.getenv(DISCORD_TOKEN_ENV)
    if not DISCORD_TOKEN:
        raise ValueError(DISCORD_TOKEN_ERR)
    client.run(DISCORD_TOKEN)
