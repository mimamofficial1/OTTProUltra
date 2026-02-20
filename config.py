import os

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

MONGO_URL = os.getenv("MONGO_URL")

LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))
FORCE_CHANNEL = os.getenv("FORCE_CHANNEL")

OWNER_ID = int(os.getenv("OWNER_ID", 0))
