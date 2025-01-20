import os
import time
import requests
from telebot import TeleBot
from handlers import register_handlers
from config import TELEGRAM_BOT_TOKEN, UPLOAD_FOLDER
from flask import Flask
from threading import Thread

app = Flask(__name__)

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize bot
bot = TeleBot(TELEGRAM_BOT_TOKEN)

# Register all handlers
register_handlers(bot)


@app.route('/')
def index():
    return "Telegram Bot is Running"


def keep_alive():
    """
    Send periodic requests to prevent the service from sleeping
    """
    while True:
        try:
            # Get your Render URL from environment variable
            url = os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:5001')
            requests.get(url)
            print("Keep alive ping sent")
        except Exception as e:
            print(f"Keep alive error: {e}")
        # Wait for 10 minutes
        time.sleep(600)


def run_bot():
    while True:
        try:
            print("Bot is starting...")
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Bot polling error: {e}")
            # Wait for 15 seconds before retrying
            time.sleep(15)


if __name__ == "__main__":
    # Start the bot in a new thread
    bot_thread = Thread(target=run_bot)
    bot_thread.start()

    # Start the keep-alive thread
    keep_alive_thread = Thread(target=keep_alive)
    keep_alive_thread.start()

    # Start the Flask app
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)