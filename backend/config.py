# backend/config.py

from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Blizzard API credentials
API_CLIENT_ID = os.getenv("BLIZZARD_CLIENT_ID")
API_SECRET = os.getenv("BLIZZARD_SECRET")

# PostgreSQL database URI
DB_URI = os.getenv("DB_URI")

# Optional: fail fast if any are missing
if not API_CLIENT_ID or not API_SECRET or not DB_URI:
    raise ValueError("Missing one or more required environment variables.")
