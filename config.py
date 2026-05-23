import os
from dotenv import load_dotenv

load_dotenv()  # 本機開發讀 .env；Zeabur 直接讀容器環境變數

DB_SERVER   = os.getenv("DB_SERVER", "")
DB_PORT     = int(os.getenv("DB_PORT", "1433"))
DB_NAME     = os.getenv("DB_NAME", "")
DB_USER     = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
CLAUDE_MODEL   = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

_missing = [k for k, v in {
    "DB_SERVER": DB_SERVER,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
    "CLAUDE_API_KEY": CLAUDE_API_KEY,
}.items() if not v]

if _missing:
    raise EnvironmentError(f"缺少必要環境變數：{', '.join(_missing)}")
