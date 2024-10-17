from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.llama_vision import process_text, process_image_and_text
from services.flux_schnell import process_image
import random
import json
import io
import requests
from datetime import datetime

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
            InlineKeyboardButton("Campus Map", callback_data="campus_map"),
            InlineKeyboardButton("Campus Food", callback_data="campus_food"),
            InlineKeyboardButton("Study Spaces", callback_data="study_spaces"),
            InlineKeyboardButton("Lost and Found", callback_data="lost_and_found")
        )
        bot.send_message(chat_id, "*Welcome to Campus Life! What would you like to know about?*", reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("campus_"))
    def campus_option_callback(call):
        if call.data == "campus_events":
            events = get_upcoming_events()
            response = "*Upcoming events:*\n" + "\n".join(f"- {event['name']} on {event['date']}" for event in events)
        elif call.data == "campus_facilities":
            facilities = get_campus_facilities()
            response = "*Campus facilities:*\n" + "\n".join(f"- {facility['name']}: {facility['status']}" for facility in facilities)
        elif call.data == "campus_clubs":
            clubs = get_student_clubs()
            response = "*Student clubs:*\n" + "\n".join(f"- {club['name']}: {club['description']}" for club in clubs)
        elif call.data == "campus_map":
            map_url = get_campus_map_url()
            response = f"*Here's a link to our interactive campus map:* [Campus Map]({map_url})"
        elif call.data == "campus_food":
            food_options = get_campus_food_options()
            response = "*Today's Campus Food Options:*\n"
            for location, menu in food_options.items():
                response += f"\n{location}:\n"
                for item in menu:
                    response += f"- {item['name']}: ${item['price']} ({item['availability']})\n"
        elif call.data == "study_spaces":
            study_spaces = get_study_spaces()
            response = "*Available Study Spaces:*\n"
            for space in study_spaces:
                response += f"\n{space['name']}: {space['available_seats']} seats available"
        elif call.data == "lost_and_found":
            response = "*Lost and Found Service*\n\nTo report a lost item or check for found items, please provide the following information:\n1. Lost or Found?\n2. Item description\n3. Date lost/found\n4. Location lost/found\n\nSeparate each piece of information with a comma."
            bot.send_message(call.message.chat.id, response, parse_mode="Markdown")
            bot.register_next_step_handler(call.message, lost_and_found_handler)
            return
        else:
            response = "*I'm sorry, I couldn't process that request.*"
        
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, response, parse_mode="Markdown")

    def lost_and_found_handler(message):
        try:
            status, description, date, location = [item.strip() for item in message.text.split(',', 3)]
            report_id = submit_lost_and_found_report(status, description, date, location)
            response = f"Thank you for your {status} item report. We have recorded the following information:\n\nReport ID: {report_id}\nItem: {description}\nDate: {date}\nLocation: {location}\n\nWe will contact you if we have any updates."
            bot.send_message(message.chat.id, response)
        except ValueError:
            bot.send_message(message.chat.id, "I'm sorry, I couldn't process that information. Please make sure you've provided all the required details separated by commas.")

    @bot.message_handler(content_types=['photo'], func=lambda message: message.caption and message.caption.lower().startswith('identify building:'))
    def identify_campus_building(message):
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_stream = io.BytesIO(downloaded_file)
        
        # Use Flux Schnell to analyze the image
        image_description = process_image(image_stream)
        
        # Use Llama Vision to identify the building and provide information
        building_info = process_image_and_text("Identify this campus building and provide information about it", image_description)
        
        bot.reply_to(message, f"*Campus Building Information:*\n\n{building_info}", parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text.lower().startswith('campus tour:'))
    def virtual_campus_tour(message):
        location = message.text[12:].strip()
        tour_description = process_text(f"Provide a detailed virtual tour description of the {location} on campus")
        
        bot.reply_to(message, f"*Virtual Campus Tour: {location}*\n\n{tour_description}", parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text.lower().startswith('campus:'))
    def handle_campus_query(message):
        query = message.text[7:].strip() # Remove 'campus:' prefix
        response = process_text(f"Campus information: {query}")
        bot.reply_to(message, f"*Here's some information about your campus query:*\n\n{response}", parse_mode="Markdown")

    # New functions to fetch real-time data
    def get_upcoming_events():
        # This function would typically make an API call to a campus events database
        # For demonstration, we'll return mock data
        return [
            {"name": "Tech Talk by Google", "date": "2024-10-20"},
            {"name": "Annual Sports Meet", "date": "2024-10-25"},
            {"name": "Cultural Fest", "date": "2024-11-01"},
            {"name": "Career Fair", "date": "2024-11-15"}
        ]

    def get_campus_facilities():
        # This function would typically make an API call to a facilities management system
        # For demonstration, we'll return mock data
        return [
            {"name": "Library", "status": "Open"},
            {"name": "Gym", "status": "Closed for maintenance"},
            {"name": "Computer Labs", "status": "Open"},
            {"name": "Cafeteria", "status": "Open"},
            {"name": "Student Center", "status": "Open"}
        ]

    def get_student_clubs():
        # This function would typically make an API call to a student organizations database
        # For demonstration, we'll return mock data
        return [
            {"name": "Robotics Club", "description": "Building the future, one robot at a time"},
            {"name": "Debate Society", "description": "Sharpening minds through intellectual discourse"},
            {"name": "Music Band", "description": "Bringing harmony to campus life"},
            {"name": "Entrepreneurship Cell", "description": "Fostering innovation and business acumen"}
        ]

    def get_campus_map_url():
        # This function would return the URL to the most up-to-date campus map
        return "https://example.com/campus-map"

    def get_campus_food_options():
        # This function would typically make an API call to the campus dining services
        # For demonstration, we'll return mock data
        return {
            "Main Cafeteria": [
                {"name": "Pizza", "price": 5.99, "availability": "In stock"},
                {"name": "Salad", "price": 4.99, "availability": "Running low"},
                {"name": "Burger", "price": 6.99, "availability": "In stock"}
            ],
            "Coffee Shop": [
                {"name": "Latte", "price": 3.99, "availability": "In stock"},
                {"name": "Muffin", "price": 2.99, "availability": "Sold out"}
            ]
        }

    def get_study_spaces():
        # This function would typically make an API call to a room reservation system
        # For demonstration, we'll return mock data with random availability
        return [
            {"name": "Main Library", "available_seats": random.randint(0, 50)},
            {"name": "Science Building Lobby", "available_seats": random.randint(0, 30)},
            {"name": "Student Union", "available_seats": random.randint(0, 40)},
            {"name": "Quiet Study Room", "available_seats": random.randint(0, 20)}
        ]

    def submit_lost_and_found_report(status, description, date, location):
        # This function would typically submit the report to a database and return a unique ID
        # For demonstration, we'll generate a mock ID
        return f"LF{random.randint(1000, 9999)}"