from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def register_start_handler(bot):
    # Register command for '/start' and '/help'
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(
            InlineKeyboardButton("Study Assistant", callback_data="study"),
            InlineKeyboardButton("Career Guide", callback_data="career"),
            InlineKeyboardButton("Campus Life", callback_data="campus"),
            InlineKeyboardButton("Social Connect", callback_data="social"),
            InlineKeyboardButton("Assignment Solver", callback_data="assignment_solver")
        )
        bot.reply_to(message, "Welcome to College Companion! How can I assist you today?", reply_markup=markup)
