import os
from telebot import TeleBot
from handlers import register_handlers
from config import TELEGRAM_BOT_TOKEN, UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize bot
bot = TeleBot(TELEGRAM_BOT_TOKEN)

# Register all handlers
register_handlers(bot)

if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)