# Telegram Summarizer Bot

A Telegram bot that summarizes articles from URLs.

## Features

- Fetches article content from a given URL.
- Uses an AI model to generate a concise summary.
- Handles long summaries by splitting them into multiple messages.

## Setup

1.  Clone the repository.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Create a `.env` file with the following variables:
    - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token.
    - `OPENROUTER_API_KEY`: Your OpenRouter API key.
    - `WEBHOOK_URL` (optional): Your webhook URL for production deployment.

## Usage

- Run the bot in development (polling mode): `python main.py`
- For production, deploy the application and set the `WEBHOOK_URL` environment variable.