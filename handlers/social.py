from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.llama_vision import process_text

def register_social_handler(bot):
    @bot.callback_query_handler(func=lambda call: call.data == "social")
    def social_callback(call):
        bot.answer_callback_query(call.id, "Opening Social Connect...")
        send_social_options(bot, call.message.chat.id)

    @bot.message_handler(commands=['social'])
    def social_command(message):
        send_social_options(bot, message.chat.id)

    def send_social_options(bot, chat_id):
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(
            InlineKeyboardButton("Find Study Partner", callback_data="find_study_partner"),
            InlineKeyboardButton("Join Interest Group", callback_data="join_interest_group"),
            InlineKeyboardButton("Upcoming Social Events", callback_data="social_events"),
            InlineKeyboardButton("Networking Tips", callback_data="networking_tips")
        )
        bot.send_message(chat_id, "*Welcome to Social Connect! How would you like to engage with your peers?*", reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data in ["find_study_partner", "join_interest_group", "social_events", "networking_tips"])
    def social_option_callback(call):
        if call.data == "find_study_partner":
            bot.answer_callback_query(call.id, "Finding Study Partner...")
            bot.send_message(call.message.chat.id, "*What subject are you looking to study? I'll try to match you with a study partner.*", parse_mode="Markdown")
        elif call.data == "join_interest_group":
            bot.answer_callback_query(call.id, "Exploring Interest Groups...")
            bot.send_message(call.message.chat.id, "*What are your interests? I can suggest some relevant campus groups.*", parse_mode="Markdown")
        elif call.data == "social_events":
            events = ["Movie Night", "Inter-College Quiz", "Volunteer Day", "International Food Festival"]
            response = "*Upcoming social events:*\n" + "\n".join(f"- {event}" for event in events)
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, response, parse_mode="Markdown")
        elif call.data == "networking_tips":
            tips = process_text("Provide 5 networking tips for college students.")
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, f"*Here are some networking tips:*\n\n{tips}", parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text.lower().startswith('social:'))
    def handle_social_query(message):
        query = message.text[7:].strip()  # Remove 'social:' prefix
        response = process_text(f"Social connection: {query}")
        bot.reply_to(message, f"*Here's some information about your social query:*\n\n{response}", parse_mode="Markdown")
