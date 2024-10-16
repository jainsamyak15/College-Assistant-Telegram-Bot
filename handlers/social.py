from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.llama_vision import process_text, process_image_and_text
from services.flux_schnell import process_image
import io
import random
import json
import logging
import time

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
            InlineKeyboardButton("Networking Tips", callback_data="networking_tips"),
            InlineKeyboardButton("Virtual Hangout", callback_data="virtual_hangout"),
            InlineKeyboardButton("Volunteer Opportunities", callback_data="volunteer_opportunities"),
            InlineKeyboardButton("Peer Mentorship", callback_data="peer_mentorship")
        )
        bot.send_message(chat_id, "*Welcome to Social Connect! How would you like to engage with your peers?*", reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data in ["find_study_partner", "join_interest_group", "social_events", "networking_tips", "virtual_hangout", "volunteer_opportunities", "peer_mentorship"])
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
        elif call.data == "virtual_hangout":
            bot.answer_callback_query(call.id, "Setting up Virtual Hangout...")
            activities = ["Movie Night", "Game Night", "Book Club", "Language Exchange", "Fitness Challenge"]
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            for activity in activities:
                markup.add(InlineKeyboardButton(activity, callback_data=f"hangout_{activity.lower().replace(' ', '_')}"))
            bot.send_message(call.message.chat.id, "*Choose a virtual hangout activity:*", reply_markup=markup, parse_mode="Markdown")
        elif call.data == "volunteer_opportunities":
            bot.answer_callback_query(call.id, "Finding Volunteer Opportunities...")
            opportunities = [
                {"name": "Local Food Bank", "date": "Next Saturday", "slots": random.randint(1, 10)},
                {"name": "Animal Shelter", "date": "This Sunday", "slots": random.randint(1, 5)},
                {"name": "Community Garden", "date": "Every Wednesday", "slots": random.randint(1, 8)},
                {"name": "Senior Center", "date": "Fridays", "slots": random.randint(1, 6)}
            ]
            response = "*Available Volunteer Opportunities:*\n"
            for opp in opportunities:
                response += f"\n{opp['name']} - {opp['date']}: {opp['slots']} slots available"
            bot.send_message(call.message.chat.id, response, parse_mode="Markdown")
        elif call.data == "peer_mentorship":
            bot.answer_callback_query(call.id, "Accessing Peer Mentorship Program...")
            bot.send_message(call.message.chat.id, "*Peer Mentorship Program*\n\nAre you interested in being a mentor or finding a mentor? Please provide the following information:\n1. Mentor or Mentee?\n2. Your major/field of study\n3. Specific areas you can help with / need help in\n4. Preferred meeting frequency (e.g., weekly, bi-weekly)\n\nSeparate each piece of information with a comma.", parse_mode="Markdown")
            bot.register_next_step_handler(call.message, peer_mentorship_handler)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("hangout_"))
    def hangout_activity_callback(call):
        activity = call.data.split("_")[1].replace("_", " ").title()
        response = f"Great choice! I've set up a virtual {activity} for tomorrow at 7 PM. Here's the link to join: [Virtual Hangout Link]"
        bot.send_message(call.message.chat.id, response)

    def peer_mentorship_handler(message):
        try:
            role, major, areas, frequency = [item.strip() for item in message.text.split(',', 3)]
            # Here you would typically save this information to a database and match mentors/mentees
            response = f"Thank you for your interest in the Peer Mentorship Program! We've recorded your information as a {role}:\n\nMajor: {major}\nAreas: {areas}\nMeeting Frequency: {frequency}\n\nWe'll be in touch soon with potential matches."
            bot.send_message(message.chat.id, response)
        except ValueError:
            bot.send_message(message.chat.id, "I'm sorry, I couldn't process that information. Please make sure you've provided all the required details separated by commas.")

    @bot.message_handler(content_types=['photo'], func=lambda message: message.caption and message.caption.lower().startswith('event poster:'))
    def analyze_event_poster(message):
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_stream = io.BytesIO(downloaded_file)
        
        # Use Flux Schnell to extract information from the event poster
        poster_info = process_image(image_stream)
        
        # Use Llama Vision to analyze the poster information and provide details
        event_details = process_image_and_text("Analyze this event poster and provide key details", poster_info)
        
        bot.reply_to(message, f"*Event Details:*\n\n{event_details}", parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text.lower().startswith('social icebreaker:'))
    def social_icebreaker(message):
        context = message.text[17:].strip()
        icebreaker = process_text(f"Generate a fun and engaging icebreaker activity for {context}")
        
        bot.reply_to(message, f"*Social Icebreaker Activity:*\n\n{icebreaker}", parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text.lower().startswith('cultural exchange:'))
    def cultural_exchange_idea(message):
        culture = message.text[17:].strip()
        idea = process_text(f"Suggest a cultural exchange activity to learn about {culture} culture")
        
        bot.reply_to(message, f"*Cultural Exchange Idea for {culture}:*\n\n{idea}", parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text.lower().startswith('social:'))
    def handle_social_query(message):
        query = message.text[7:].strip() # Remove 'social:' prefix
        response = process_text(f"Social connection: {query}")
        bot.reply_to(message, f"*Here's some information about your social query:*\n\n{response}", parse_mode="Markdown")
