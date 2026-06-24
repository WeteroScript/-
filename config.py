import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAX_THREADS = int(os.getenv("MAX_THREADS", 500))
TIMEOUT = int(os.getenv("TIMEOUT", 3))
