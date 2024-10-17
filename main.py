import os
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

def run_bot():
    print("Bot is running...")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # Start the bot in a new thread
    Thread(target=run_bot).start()
    
    # Start the Flask app (Render requires this to keep the service running)
    port = int(os.environ.get("PORT", 5001))  # Render sets this environment variable
    app.run(host='0.0.0.0', port=port)
