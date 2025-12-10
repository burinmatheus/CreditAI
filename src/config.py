import os
from dotenv import load_dotenv

load_dotenv()

# Application Configuration
APP_PORT = int(os.getenv("APP_PORT", "8000"))
