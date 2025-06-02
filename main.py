import discord
import os
from dotenv import load_dotenv

# Import all command modules from the organized structure
from commands import (
    register_team,
    unregister_team,
    team_details,
    update_team_group,
    join_team,
    leave_team,
    add_team_member,
    remove_team_member
)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

# Register all commands
tree.add_command(register_team)
tree.add_command(unregister_team)
tree.add_command(team_details)
tree.add_command(update_team_group)
tree.add_command(join_team)
tree.add_command(leave_team)
tree.add_command(add_team_member)
tree.add_command(remove_team_member)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    # Sync commands to the specific guild
    synced = await tree.sync()
    print(f'Synced {len(synced)} commands')


if __name__ == "__main__":
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    if not DISCORD_TOKEN:
        raise ValueError(
            "DISCORD_TOKEN must be set in the environment variables.")
    client.run(DISCORD_TOKEN)
