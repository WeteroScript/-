import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAX_THREADS = int(os.getenv("MAX_THREADS", 2000))   # увеличен до 2000
TIMEOUT = int(os.getenv("TIMEOUT", 1))              # таймаут 1 сек
SYN_COUNT_RATIO = 0.5    # 50% на SYN
ICMP_COUNT_RATIO = 0.25  # 25% на ICMP
