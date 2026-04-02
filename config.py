import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# دیاریکردنی پاشگر بەپێی سیستەمی ویندۆز یان لینوکس
EXE_EXT = ".exe" if os.name == 'nt' else ""

# Telegram configurations
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Database and Logging
DB_PATH = "hunter_state.db"
LOG_FILE = "hunter.log"
