import asyncio
from bot import SummarizerBot
from config import WEBHOOK_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    bot = SummarizerBot()
    
    if WEBHOOK_URL:
        logger.info("Running in webhook mode")
        return bot.get_app()
    else:
        logger.info("Running in polling mode (development)")
        bot.run_polling()

if __name__ == "__main__":
    main()