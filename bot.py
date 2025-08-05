import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from summarizer import ArticleSummarizer
from config import TELEGRAM_BOT_TOKEN
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SummarizerBot:
    def __init__(self):
        self.summarizer = ArticleSummarizer()
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    def is_valid_url(self, text: str) -> bool:
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        return bool(url_pattern.search(text))

    def extract_url(self, text: str) -> str:
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        match = url_pattern.search(text)
        return match.group() if match else ""

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_message = """
🤖 **Personal Article Summarizer Bot**

Send me any article URL and I'll provide you with:
• Core thesis and main argument
• Key points and insights
• Bottom line takeaway
• Whether it's worth your time

Just paste a URL and I'll get to work! 📝

Use /help for more information.
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_message = """
📖 **How to use this bot:**

1. **Send a URL**: Just paste any article URL from blogs, news sites, or publications
2. **Wait for analysis**: I'll extract the content and create an analytical summary
3. **Get insights**: Receive a structured summary to help you decide if it's worth reading

**Supported sites**: Most news sites, blogs, and publications (Hacker News links, Medium, etc.)

**Tips**:
• Works best with text-heavy articles
• May not work with paywalled content
• Processing takes 10-30 seconds depending on article length

Having issues? Make sure you're sending a complete URL starting with http:// or https://
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_text = update.message.text
        
        if not self.is_valid_url(message_text):
            await update.message.reply_text(
                "🤔 I don't see a valid URL in your message. Please send me a link to an article you'd like summarized!\n\n"
                "Example: https://example.com/article-title"
            )
            return

        url = self.extract_url(message_text)
        processing_message = await update.message.reply_text("🔄 Analyzing article... This may take a moment.")
        
        try:
            summary = await self.summarizer.process_url(url)
            
            TELEGRAM_MAX_LENGTH = 4096
            
            header = "📄 **Article Summary**\n\n"
            
            if len(header) + len(summary) > TELEGRAM_MAX_LENGTH:
                logger.info("Summary is too long, splitting into multiple messages.")
                
                available_length = TELEGRAM_MAX_LENGTH - len(header)
                first_chunk = summary[:available_length]
                
                last_newline = first_chunk.rfind('\n')
                if last_newline != -1:
                    first_chunk = first_chunk[:last_newline]
                    
                await processing_message.edit_text(
                    f"{header}{first_chunk}",
                    parse_mode='Markdown'
                )

                remaining_summary = summary[len(first_chunk):].strip()
                
                for i in range(0, len(remaining_summary), TELEGRAM_MAX_LENGTH):
                    chunk = remaining_summary[i:i + TELEGRAM_MAX_LENGTH]
                    await update.message.reply_text(
                        chunk,
                        parse_mode='Markdown'
                    )
            else:
                await processing_message.edit_text(
                    f"{header}{summary}",
                    parse_mode='Markdown'
                )
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {type(e).__name__} - {str(e)}")
            await processing_message.edit_text(
                f"❌ Sorry, I couldn't process that article. This might be due to:\n\n"
                f"• Paywall or login required\n"
                f"• Site blocking automated access\n"
                f"• Technical issues or an invalid response\n\n"
                f"Please try a different article or check if the URL is accessible."
            )

    def run_polling(self):
        logger.info("Starting bot with polling...")
        self.application.run_polling()

    async def set_webhook(self, webhook_url: str):
        await self.application.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")

    def get_app(self):
        return self.application