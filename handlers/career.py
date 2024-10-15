from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.llama_vision import process_text

def register_career_handler(bot):
    @bot.callback_query_handler(func=lambda call: call.data == "career")
    def career_callback(call):
        bot.answer_callback_query(call.id, "Opening Career Guide...")
        send_career_options(bot, call.message.chat.id)

    @bot.message_handler(commands=['career'])
    def career_command(message):
        send_career_options(bot, message.chat.id)

    def send_career_options(bot, chat_id):
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(
            InlineKeyboardButton("Resume Review", callback_data="resume_review"),
            InlineKeyboardButton("Job Search", callback_data="job_search"),
            InlineKeyboardButton("Interview Tips", callback_data="interview_tips"),
            InlineKeyboardButton("Career Path", callback_data="career_path")
        )
        bot.send_message(chat_id, "*Welcome to the Career Guide! How can I assist you today?*", reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data in ["resume_review", "job_search", "interview_tips", "career_path"])
    def career_option_callback(call):
        if call.data == "resume_review":
            bot.answer_callback_query(call.id, "Opening Resume Review...")
            bot.send_message(call.message.chat.id, "*Please upload your resume as a PDF file for review.*", parse_mode="Markdown")
        elif call.data == "job_search":
            bot.answer_callback_query(call.id, "Opening Job Search...")
            bot.send_message(call.message.chat.id, "*What kind of job are you looking for? Please provide details like industry, position, and location.*", parse_mode="Markdown")
        elif call.data == "interview_tips":
            bot.answer_callback_query(call.id, "Providing Interview Tips...")
            tips = process_text("Provide 5 key interview tips for college students.")
            bot.send_message(call.message.chat.id, f"*Here are some interview tips:*\n\n{tips}", parse_mode="Markdown")
        elif call.data == "career_path":
            bot.answer_callback_query(call.id, "Exploring Career Paths...")
            bot.send_message(call.message.chat.id, "*What's your major or field of interest? I can suggest potential career paths based on that.*", parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text.lower().startswith('career:'))
    def handle_career_query(message):
        query = message.text[7:].strip()  # Remove 'career:' prefix
        response = process_text(f"Career advice: {query}")
        bot.reply_to(message, f"*Here's some career advice based on your query:*\n\n{response}", parse_mode="Markdown")
