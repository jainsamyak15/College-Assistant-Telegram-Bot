import os
from dotenv import load_dotenv

# Print the current working directory
print(f"Current working directory: {os.getcwd()}")

# Load the .env file
load_dotenv()

# Get the bot token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')

# Print the bot token (be careful with this in production!)
print(f"Bot token: {TELEGRAM_BOT_TOKEN}")
# Add this line
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in the environment variables")

if not TOGETHER_API_KEY:
    raise ValueError("TOGETHER_API_KEY is not set in the environment variables")

GOOGLE_SHEETS_CREDENTIALS = '/Users/samyakjain/All Codes/college_assistant_bot/credentials.json'
