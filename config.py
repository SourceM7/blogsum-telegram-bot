import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL_NAME = "llama-3.3-70b-versatile"