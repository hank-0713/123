import os
from dotenv import load_dotenv

load_dotenv()

DB_SERVER = os.environ["DB_SERVER"]
DB_PORT = int(os.environ["DB_PORT"])
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
