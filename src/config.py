import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080").rstrip('/')
CAFE_API_KEY = os.getenv("CAFE_API_KEY")
AUDIT_GROUP_ID = os.getenv("AUDIT_GROUP_ID")
PROXY_URL = os.getenv("PROXY_URL")

# Backend API Base URL
API_BASE_URL = f"{BACKEND_URL}/api/v1"

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables.")
