import os
from dotenv import load_dotenv
from strings import *

load_dotenv()

TEAM_THREAD_PARENT_ID = os.getenv(TEAM_THREAD_PARENT_ID_ENV)
if not TEAM_THREAD_PARENT_ID or not TEAM_THREAD_PARENT_ID.isdigit():
    raise ValueError(TEAM_THREAD_PARENT_ID_ERR)
TEAM_THREAD_PARENT_ID = int(TEAM_THREAD_PARENT_ID)


