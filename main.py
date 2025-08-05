import asyncio
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from bot import SummarizerBot
from config import WEBHOOK_URL, TELEGRAM_BOT_TOKEN
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = SummarizerBot()
ptb_app = bot.get_app()

async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    await ptb_app.initialize()
    await ptb_app.bot.set_webhook(
        url=f"{WEBHOOK_URL}/webhook/{TELEGRAM_BOT_TOKEN}",
        allowed_updates=Update.ALL_TYPES
    )
    await ptb_app.start()
    yield
    logger.info("Shutting down...")
    await ptb_app.stop()

app = FastAPI(lifespan=lifespan)

@app.post(f"/webhook/{TELEGRAM_BOT_TOKEN}")
async def webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, ptb_app.bot)
        await ptb_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return {"status": "error"}

@app.get("/")
def index():
    return {"status": "ok"}

def main():
    if WEBHOOK_URL:
        logger.info("Running in webhook mode")
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port
        )
    else:
        logger.info("Running in polling mode (development)")
        bot.run_polling()

if __name__ == "__main__":
    main()
