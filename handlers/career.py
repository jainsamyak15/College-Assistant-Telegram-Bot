import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.llama_vision import process_text, process_image_and_text
from services.flux_schnell import process_image
from services.document_generator import generate_cover_letter
from telebot.apihelper import ApiTelegramException
from utils.google_sheets_logger import GoogleSheetsLogger
import json
import io
import PyPDF2
import re
import traceback
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()
GOOGLE_SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
GOOGLE_SHEETS_SPREADSHEET_ID = '1CC0MvsG65IGV1rhRK6q2ORi0iiX93TX1Fk91V4ImO7Q'
# Initialize Google Sheets Logger
try:
    sheets_logger = GoogleSheetsLogger(GOOGLE_SHEETS_CREDENTIALS, GOOGLE_SHEETS_SPREADSHEET_ID)

except Exception as e:
    logger.error(f"Failed to initialize Google Sheets logger: {str(e)}")
    sheets_logger = None


def register_career_handler(bot):
    @bot.callback_query_handler(func=lambda call: call.data == "career")
    def career_callback(call):
        try:
            bot.answer_callback_query(call.id, "Opening Career Guide...")
            send_career_options(bot, call.message.chat.id)

            if sheets_logger:
                sheets_logger.log_interaction(
                    user_id=call.from_user.id,
                    username=call.from_user.username,
                    query_type="career_menu",
                    user_query="Opened career menu",
                    ai_response="Displayed career options menu"
                )
        except Exception as e:
            logger.error(f"Error in career callback: {str(e)}")

    @bot.message_handler(commands=['career'])
    def career_command(message):
        try:
            send_career_options(bot, message.chat.id)

            if sheets_logger:
                sheets_logger.log_interaction(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    query_type="career_command",
                    user_query="/career",
                    ai_response="Displayed career options menu"
                )
        except Exception as e:
            logger.error(f"Error in career command: {str(e)}")

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
            InlineKeyboardButton("Industry Insights", callback_data="industry_insights"),
            InlineKeyboardButton("Mock Interview", callback_data="mock_interview")
        )
        bot.send_message(chat_id, "*Welcome to the Career Guide! How can I assist you today?*", reply_markup=markup,
                         parse_mode="Markdown")

    @bot.callback_query_handler(
        func=lambda call: call.data in ["resume_review", "job_search", "interview_tips", "career_path",
                                        "salary_negotiation", "cover_letter_generator", "industry_insights",
                                        "mock_interview"])
    def career_option_callback(call):
        try:
            response = ""
            if call.data == "resume_review":
                response = resume_review_callback(call)
            elif call.data == "job_search":
                bot.answer_callback_query(call.id, "Opening Job Search...")
                response = "*What kind of job are you looking for? Please provide details like industry, position, and location.*"
                bot.send_message(call.message.chat.id, response, parse_mode="Markdown")
            elif call.data == "interview_tips":
                bot.answer_callback_query(call.id, "Providing Interview Tips...")
                tips = process_text("Provide 5 key interview tips for college students.")
                response = f"*Here are some interview tips:*\n\n{tips}"
                bot.send_message(call.message.chat.id, response, parse_mode="Markdown")
            elif call.data == "career_path":
                bot.answer_callback_query(call.id, "Exploring Career Paths...")
                response = "*What's your major or field of interest? I can suggest potential career paths based on that.*"
                bot.send_message(call.message.chat.id, response, parse_mode="Markdown")
            elif call.data == "salary_negotiation":
                bot.answer_callback_query(call.id, "Opening Salary Negotiation Guide...")
                tips = process_text("Provide 5 key salary negotiation tips for new graduates.")
                response = f"*Salary Negotiation Tips:*\n\n{tips}"
                bot.send_message(call.message.chat.id, response, parse_mode="Markdown")
            elif call.data == "cover_letter_generator":
                bot.answer_callback_query(call.id, "Opening Cover Letter Generator...")
                response = "*Please provide the following information for your cover letter:*\n1. Your name\n2. The company name\n3. The position you're applying for\n4. Your top 3 skills\n\nSeparate each piece of information with a comma."
                bot.send_message(call.message.chat.id, response, parse_mode="Markdown")
                bot.register_next_step_handler(call.message, generate_cover_letter_handler)
            elif call.data == "industry_insights":
                bot.answer_callback_query(call.id, "Fetching Industry Insights...")
                markup = InlineKeyboardMarkup()
                markup.row_width = 2
                industries = ["Tech", "Finance", "Healthcare", "Education", "Entertainment"]
                for industry in industries:
                    markup.add(InlineKeyboardButton(industry, callback_data=f"insight_{industry.lower()}"))
                response = "*Select an industry for insights:*"
                bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode="Markdown")
            elif call.data == "mock_interview":
                bot.answer_callback_query(call.id, "Starting Mock Interview...")
                response = "*What position or field would you like to practice interviewing for?*"
                bot.send_message(call.message.chat.id, response, parse_mode="Markdown")
                bot.register_next_step_handler(call.message, start_mock_interview)

            if sheets_logger:
                sheets_logger.log_interaction(
                    user_id=call.from_user.id,
                    username=call.from_user.username,
                    query_type=f"career_option_{call.data}",
                    user_query=f"Selected {call.data}",
                    ai_response=response
                )

        except Exception as e:
            logger.error(f"Error in career option callback: {str(e)}")
            bot.reply_to(call.message, "An error occurred while processing your request. Please try again.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("insight_"))
    def industry_insight_callback(call):
        try:
            industry = call.data.split("_")[1]
            insights = process_text(f"Provide 3 key insights about the current job market in the {industry} industry.")
            response = f"*Industry Insights for {industry.capitalize()}:*\n\n{insights}"
            bot.send_message(call.message.chat.id, response, parse_mode="Markdown")

            if sheets_logger:
                sheets_logger.log_interaction(
                    user_id=call.from_user.id,
                    username=call.from_user.username,
                    query_type="industry_insight",
                    user_query=f"Requested insights for {industry}",
                    ai_response=response
                )
        except Exception as e:
            logger.error(f"Error in industry insight callback: {str(e)}")

    def generate_cover_letter_handler(message):
        try:
            name, company, position, skills = [item.strip() for item in message.text.split(',', 3)]
            cover_letter = generate_cover_letter(name, company, position, skills)
            response = f"*Here's your generated cover letter:*\n\n{cover_letter}"
            bot.send_message(message.chat.id, response, parse_mode="Markdown")

            if sheets_logger:
                sheets_logger.log_interaction(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    query_type="cover_letter",
                    user_query=f"Generated cover letter for {position} at {company}",
                    ai_response=response
                )
        except ValueError:
            error_msg = "I'm sorry, I couldn't process that information. Please make sure you've provided all the required details separated by commas."
            bot.send_message(message.chat.id, error_msg)

    @bot.message_handler(content_types=['photo'],
                         func=lambda message: message.caption and message.caption.lower().startswith('analyze resume:'))
    def analyze_resume_image(message):
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            image_stream = io.BytesIO(downloaded_file)

            extracted_text = process_image(image_stream)
            analysis = process_image_and_text("Analyze this resume and provide feedback", extracted_text)
            response = f"*Resume Analysis:*\n\n{analysis}"

            bot.reply_to(message, response, parse_mode="Markdown")

            if sheets_logger:
                sheets_logger.log_interaction(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    query_type="resume_analysis_image",
                    user_query="Analyzed resume from image",
                    ai_response=response
                )
        except Exception as e:
            logger.error(f"Error analyzing resume image: {str(e)}")
            bot.reply_to(message, "There was an error analyzing your resume image. Please try again.")

    def start_mock_interview(message):
        try:
            position = message.text.strip()
            interview_questions = process_text(f"Generate 3 challenging interview questions for a {position} position")
            response = f"*Mock Interview for {position} position:*\n\n{interview_questions}\n\nPlease answer these questions, and I'll provide feedback on your responses."

            bot.send_message(message.chat.id, response, parse_mode="Markdown")
            bot.register_next_step_handler(message, mock_interview_feedback)

            if sheets_logger:
                sheets_logger.log_interaction(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    query_type="mock_interview_start",
                    user_query=f"Started mock interview for {position}",
                    ai_response=response
                )
        except Exception as e:
            logger.error(f"Error starting mock interview: {str(e)}")
            bot.reply_to(message, "An error occurred while starting the mock interview. Please try again.")

    def mock_interview_feedback(message):
        try:
            feedback = process_text(
                f"Evaluate this interview response and provide constructive feedback: {message.text}")
            response = f"*Interview Response Feedback:*\n\n{feedback}"
            bot.reply_to(message, response, parse_mode="Markdown")

            if sheets_logger:
                sheets_logger.log_interaction(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    query_type="mock_interview_feedback",
                    user_query=message.text,
                    ai_response=response
                )
        except Exception as e:
            logger.error(f"Error providing interview feedback: {str(e)}")
            bot.reply_to(message, "An error occurred while generating feedback. Please try again.")

    @bot.message_handler(func=lambda message: message.text.lower().startswith('career:'))
    def handle_career_query(message):
        try:
            query = message.text[7:].strip()  # Remove 'career:' prefix
            response = process_text(f"Career advice: {query}")
            bot.reply_to(message, f"*Here's some career advice based on your query:*\n\n{response}",
                         parse_mode="Markdown")

            if sheets_logger:
                sheets_logger.log_interaction(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    query_type="career_advice",
                    user_query=query,
                    ai_response=response
                )
        except Exception as e:
            logger.error(f"Error handling career query: {str(e)}")
            bot.reply_to(message, "An error occurred while processing your query. Please try again.")

    def resume_review_callback(call):
        try:
            logger.info(f"User {call.from_user.id} requested resume review")
            bot.answer_callback_query(call.id, "Opening Resume Review...")
            response = "*Please upload your resume as a PDF file, image, or document for review.*"
            bot.send_message(call.message.chat.id, response, parse_mode="Markdown")
            bot.register_next_step_handler(call.message, handle_resume_upload)
            return response
        except Exception as e:
            logger.error(f"Error in resume review callback: {str(e)}")
            raise

    def handle_resume_upload(message):
        try:
            logger.info(f"Starting resume processing for user {message.from_user.id}")
            extracted_text = ""

            if message.document:
                logger.info(f"Processing document for user {message.from_user.id}")
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)

                if message.document.mime_type == "application/pdf":
                    pdf_stream = io.BytesIO(downloaded_file)
                    pdf_reader = PyPDF2.PdfReader(pdf_stream)
                    extracted_text = "\n".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
                else:
                    extracted_text = process_image(io.BytesIO(downloaded_file))

            elif message.photo:
                logger.info(f"Processing photo for user {message.from_user.id}")
                file_info = bot.get_file(message.photo[-1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                extracted_text = process_image(io.BytesIO(downloaded_file))

            else:
                response = "Please upload a PDF, image, or document."
                bot.reply_to(message, response)
                return

            bot.reply_to(message, "Resume received! Reviewing...")

            logger.info(f"Extracted text from resume for user {message.from_user.id}")

            analysis = process_image_and_text("Analyze this resume and provide feedback", extracted_text)
            ats_score = calculate_ats_score(extracted_text)

            response = f"*Resume Analysis:*\n\n{analysis}\n\nATS Score: *{ats_score}/100*"
            bot.reply_to(message, response, parse_mode="Markdown")

            if sheets_logger:
                sheets_logger.log_interaction(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    query_type="resume_upload",
                    user_query="Uploaded resume for analysis",
                    ai_response=response
                )

        except Exception as e:
            logger.error(f"Error processing resume upload: {str(e)}")
            bot.reply_to(message, "There was an error processing your resume. Please try again.")


    def calculate_ats_score(resume_text):
        """
        Calculate ATS score based on resume content
        """
        try:
            # Keywords for job-relevant skills, experience, etc.
            keywords = ['experience', 'skills', 'education', 'projects', 'certification',
                        'achievement', 'leadership', 'management', 'technical', 'professional']

            section_keywords = ['work experience', 'education', 'skills', 'projects',
                                'certifications', 'achievements', 'summary', 'objective']

            format_keywords = ['email', 'phone', 'address', 'linkedin']

            total_keywords = len(keywords)
            total_sections = len(section_keywords)
            total_format = len(format_keywords)

            # Initialize score components
            keyword_score = 0
            section_score = 0
            format_score = 0

            # Calculate keyword score (40%)
            for keyword in keywords:
                if keyword.lower() in resume_text.lower():
                    keyword_score += 1
            keyword_score = min(int((keyword_score / total_keywords) * 40), 40)

            # Calculate section score (40%)
            for section in section_keywords:
                if section.lower() in resume_text.lower():
                    section_score += 1
            section_score = min(int((section_score / total_sections) * 40), 40)

            # Calculate format score (20%)
            for format_item in format_keywords:
                if format_item.lower() in resume_text.lower():
                    format_score += 1
            format_score = min(int((format_score / total_format) * 20), 20)

            # Apply penalties
            penalties = 0

            # Penalty for missing key sections
            if section_score < (total_sections * 0.6):  # Less than 60% of key sections
                penalties += 10

            # Penalty for poor formatting (based on newlines and spacing)
            if resume_text.count('\n') < 10:  # Too few line breaks
                penalties += 5

            # Calculate final score
            final_score = keyword_score + section_score + format_score - penalties

            # Ensure score is within 0-100 range
            return max(0, min(final_score, 100))

        except Exception as e:
            logger.error(f"Error calculating ATS score: {str(e)}")
            return 0


    def sanitize_markdown(text):
        """
        Remove or escape Markdown formatting characters
        """
        try:
            # List of characters to escape
            markdown_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

            # Escape each character
            for char in markdown_chars:
                text = text.replace(char, '\\' + char)

            return text
        except Exception as e:
            logger.error(f"Error sanitizing markdown: {str(e)}")
            return text


    def extract_text_from_pdf(file_stream):
        """
        Extract text content from a PDF file
        """
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_stream))
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise


    @bot.message_handler(func=lambda message: message.text and message.text.lower().startswith('analyze career path:'))
    def analyze_career_path(message):
        try:
            query = message.text[19:].strip()  # Remove 'analyze career path:' prefix
            analysis = process_text(f"Analyze career path and provide guidance for: {query}")
            response = f"*Career Path Analysis:*\n\n{analysis}"
            bot.reply_to(message, response, parse_mode="Markdown")

            if sheets_logger:
                sheets_logger.log_interaction(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    query_type="career_path_analysis",
                    user_query=query,
                    ai_response=response
                )
        except Exception as e:
            logger.error(f"Error analyzing career path: {str(e)}")
            bot.reply_to(message, "An error occurred while analyzing your career path. Please try again.")


    @bot.message_handler(func=lambda message: message.text and message.text.lower().startswith('job market:'))
    def analyze_job_market(message):
        try:
            query = message.text[11:].strip()  # Remove 'job market:' prefix
            analysis = process_text(f"Analyze job market trends and opportunities for: {query}")
            response = f"*Job Market Analysis:*\n\n{analysis}"
            bot.reply_to(message, response, parse_mode="Markdown")

            if sheets_logger:
                sheets_logger.log_interaction(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    query_type="job_market_analysis",
                    user_query=query,
                    ai_response=response
                )
        except Exception as e:
            logger.error(f"Error analyzing job market: {str(e)}")
            bot.reply_to(message, "An error occurred while analyzing the job market. Please try again.")


    return bot