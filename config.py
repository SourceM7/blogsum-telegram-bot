import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "z-ai/glm-4.5-air:free"