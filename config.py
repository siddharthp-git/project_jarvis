"""
Global configuration for Project Jarvis.
Loads environment variables from .env for sensitive credentials.
"""
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
MODEL = os.environ.get("MODEL", "gemma4:e2b")
MAX_TOOL_ROUNDS = int(os.environ.get("MAX_TOOL_ROUNDS", 5))
CONVERSATION_HISTORY_LIMIT = int(os.environ.get("CONVERSATION_HISTORY_LIMIT", 30))
TIMEOUT = int(os.environ.get("TIMEOUT", 180))
WAKE_WORD = os.environ.get("WAKE_WORD", "hello")

# Tavily — get a free key at https://app.tavily.com
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "YOUR_TAVILY_KEY")

# NewsAPI — get a free key at https://newsapi.org
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "YOUR_NEWS_API_KEY")

# ─── Gmail SMTP (for send_email tool) ────────────────────────────
# Use your Gmail address and a Google App Password (NOT your regular password).
# Create one at: https://myaccount.google.com/apppasswords
GMAIL_ADDRESS  = os.environ.get("GMAIL_ADDRESS",  "YOUR_GMAIL@gmail.com")
GMAIL_APP_PASS = os.environ.get("GMAIL_APP_PASS", "YOUR_APP_PASSWORD_HERE")
