import os
from dotenv import load_dotenv

load_dotenv()

TEAM_THREAD_PARENT_ID = os.getenv('TEAM_THREAD_PARENT_ID')
if not TEAM_THREAD_PARENT_ID or not TEAM_THREAD_PARENT_ID.isdigit():
    raise ValueError(
        "TEAM_THREAD_PARENT_ID must be set and must be a valid integer.")
TEAM_THREAD_PARENT_ID = int(TEAM_THREAD_PARENT_ID)
