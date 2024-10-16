# career.py

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.llama_vision import process_text, process_image_and_text
from services.flux_schnell import process_image
from services.document_generator import generate_cover_letter
import json
import io

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
            InlineKeyboardButton("Career Path", callback_data="career_path"),
            InlineKeyboardButton("Salary Negotiation", callback_data="salary_negotiation"),
            InlineKeyboardButton("Cover Letter Generator", callback_data="cover_letter_generator"),
            InlineKeyboardButton("Industry Insights", callback_data="industry_insights")
        )
        bot.send_message(chat_id, "*Welcome to the Career Guide! How can I assist you today?*", reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data in ["resume_review", "job_search", "interview_tips", "career_path", "salary_negotiation", "cover_letter_generator", "industry_insights"])
    def career_option_callback(call):
        if call.data == "resume_review":
            bot.answer_callback_query(call.id, "Opening Resume Review...")
            bot.send_message(call.message.chat.id, "*Please upload your resume as a PDF file or image for review.*", parse_mode="Markdown")
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
        elif call.data == "salary_negotiation":
            bot.answer_callback_query(call.id, "Opening Salary Negotiation Guide...")
            tips = process_text("Provide 5 key salary negotiation tips for new graduates.")
            bot.send_message(call.message.chat.id, f"*Salary Negotiation Tips:*\n\n{tips}", parse_mode="Markdown")
        elif call.data == "cover_letter_generator":
            bot.answer_callback_query(call.id, "Opening Cover Letter Generator...")
            bot.send_message(call.message.chat.id, "*Please provide the following information for your cover letter:*\n1. Your name\n2. The company name\n3. The position you're applying for\n4. Your top 3 skills\n\nSeparate each piece of information with a comma.", parse_mode="Markdown")
            bot.register_next_step_handler(call.message, generate_cover_letter_handler)
        elif call.data == "industry_insights":
            bot.answer_callback_query(call.id, "Fetching Industry Insights...")
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            industries = ["Tech", "Finance", "Healthcare", "Education", "Entertainment"]
            for industry in industries:
                markup.add(InlineKeyboardButton(industry, callback_data=f"insight_{industry.lower()}"))
            bot.send_message(call.message.chat.id, "*Select an industry for insights:*", reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("insight_"))
    def industry_insight_callback(call):
        industry = call.data.split("_")[1]
        insights = process_text(f"Provide 3 key insights about the current job market in the {industry} industry.")
        bot.send_message(call.message.chat.id, f"*Industry Insights for {industry.capitalize()}:*\n\n{insights}", parse_mode="Markdown")

    def generate_cover_letter_handler(message):
        try:
            name, company, position, skills = [item.strip() for item in message.text.split(',', 3)]
            cover_letter = generate_cover_letter(name, company, position, skills)
            bot.send_message(message.chat.id, f"*Here's your generated cover letter:*\n\n{cover_letter}", parse_mode="Markdown")
        except ValueError:
            bot.send_message(message.chat.id, "I'm sorry, I couldn't process that information. Please make sure you've provided all the required details separated by commas.")

    @bot.message_handler(content_types=['photo'], func=lambda message: message.caption and message.caption.lower().startswith('analyze resume:'))
    def analyze_resume_image(message):
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_stream = io.BytesIO(downloaded_file)
        
        # Use Flux Schnell to extract text from the resume image
        extracted_text = process_image(image_stream)
        
        # Use Llama Vision to analyze the extracted text
        analysis = process_image_and_text("Analyze this resume and provide feedback", extracted_text)
        
        bot.reply_to(message, f"*Resume Analysis:*\n\n{analysis}", parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text.lower().startswith('mock interview:'))
    def mock_interview(message):
        topic = message.text[15:].strip()
        interview_questions = process_text(f"Generate 3 challenging interview questions for a {topic} position")
        
        bot.reply_to(message, f"*Mock Interview for {topic} position:*\n\n{interview_questions}\n\nPlease answer these questions, and I'll provide feedback on your responses.", parse_mode="Markdown")
        bot.register_next_step_handler(message, mock_interview_feedback)

    def mock_interview_feedback(message):
        feedback = process_text(f"Evaluate this interview response and provide constructive feedback: {message.text}")
        bot.reply_to(message, f"*Interview Response Feedback:*\n\n{feedback}", parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text.lower().startswith('career:'))
    def handle_career_query(message):
        query = message.text[7:].strip() # Remove 'career:' prefix
        response = process_text(f"Career advice: {query}")
        bot.reply_to(message, f"*Here's some career advice based on your query:*\n\n{response}", parse_mode="Markdown")
