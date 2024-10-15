from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.llama_vision import process_text
import random

def register_campus_handler(bot):
    @bot.callback_query_handler(func=lambda call: call.data == "campus")
    def campus_callback(call):
        bot.answer_callback_query(call.id, "Opening Campus Life...")
        send_campus_options(bot, call.message.chat.id)

    @bot.message_handler(commands=['campus'])
    def campus_command(message):
        send_campus_options(bot, message.chat.id)

    def send_campus_options(bot, chat_id):
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(
            InlineKeyboardButton("Events", callback_data="campus_events"),
            InlineKeyboardButton("Facilities", callback_data="campus_facilities"),
            InlineKeyboardButton("Clubs", callback_data="campus_clubs"),
            InlineKeyboardButton("Campus Map", callback_data="campus_map")
        )
        bot.send_message(chat_id, "*Welcome to Campus Life! What would you like to know about?*", reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("campus_"))
    def campus_option_callback(call):
        if call.data == "campus_events":
            events = ["Tech Talk by Google", "Annual Sports Meet", "Cultural Fest", "Career Fair"]
            response = "*Upcoming events:*\n" + "\n".join(f"- {event}" for event in events)
        elif call.data == "campus_facilities":
            facilities = ["Library", "Gym", "Computer Labs", "Cafeteria", "Student Center"]
            response = "*Campus facilities:*\n" + "\n".join(f"- {facility}" for facility in facilities)
        elif call.data == "campus_clubs":
            clubs = ["Robotics Club", "Debate Society", "Music Band", "Entrepreneurship Cell"]
            response = "*Student clubs:*\n" + "\n".join(f"- {club}" for club in clubs)
        elif call.data == "campus_map":
            response = "*Here's a link to our interactive campus map:* [Campus Map Link]"
        else:
            response = "*I'm sorry, I couldn't process that request.*"
        
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, response, parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text.lower().startswith('campus:'))
    def handle_campus_query(message):
        query = message.text[7:].strip()  # Remove 'campus:' prefix
        response = process_text(f"Campus information: {query}")
        bot.reply_to(message, f"*Here's some information about your campus query:*\n\n{response}", parse_mode="Markdown")
