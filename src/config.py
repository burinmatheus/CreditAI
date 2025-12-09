import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "creditai")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "creditai_dev")
POSTGRES_DB = os.getenv("POSTGRES_DB", "creditai_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Application Configuration
APP_PORT = int(os.getenv("APP_PORT", "8000"))
