import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.llama_vision import process_text, process_image_and_text
from services.flux_schnell import process_image
from services.document_generator import generate_cover_letter
from telebot.apihelper import ApiTelegramException
import json
import io
import PyPDF2
import re
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
            InlineKeyboardButton("Industry Insights", callback_data="industry_insights"),
            InlineKeyboardButton("Mock Interview", callback_data="mock_interview")
        )
        bot.send_message(chat_id, "*Welcome to the Career Guide! How can I assist you today?*", reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data in ["resume_review", "job_search", "interview_tips", "career_path", "salary_negotiation", "cover_letter_generator", "industry_insights", "mock_interview"])
    def career_option_callback(call):
        try:
            if call.data == "resume_review":
                resume_review_callback(call)
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
            elif call.data == "mock_interview":
                bot.answer_callback_query(call.id, "Starting Mock Interview...")
                bot.send_message(call.message.chat.id, "*What position or field would you like to practice interviewing for?*", parse_mode="Markdown")
                bot.register_next_step_handler(call.message, start_mock_interview)
        except Exception as e:
            logger.error(f"Error in career option callback: {str(e)}")
            bot.reply_to(call.message.chat.id, "An error occurred while processing your request. Please try again.")

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
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            image_stream = io.BytesIO(downloaded_file)
            
            extracted_text = process_image(image_stream)
            analysis = process_image_and_text("Analyze this resume and provide feedback", extracted_text)
            
            bot.reply_to(message, f"*Resume Analysis:*\n\n{analysis}", parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error analyzing resume image: {str(e)}")
            bot.reply_to(message, "There was an error analyzing your resume image. Please try again.")

    def start_mock_interview(message):
        position = message.text.strip()
        interview_questions = process_text(f"Generate 3 challenging interview questions for a {position} position")
        
        bot.send_message(message.chat.id, f"*Mock Interview for {position} position:*\n\n{interview_questions}\n\nPlease answer these questions, and I'll provide feedback on your responses.", parse_mode="Markdown")
        bot.register_next_step_handler(message, mock_interview_feedback)

    def mock_interview_feedback(message):
        feedback = process_text(f"Evaluate this interview response and provide constructive feedback: {message.text}")
        bot.reply_to(message, f"*Interview Response Feedback:*\n\n{feedback}", parse_mode="Markdown")

    @bot.message_handler(func=lambda message: message.text.lower().startswith('career:'))
    def handle_career_query(message):
        query = message.text[7:].strip()  # Remove 'career:' prefix
        response = process_text(f"Career advice: {query}")
        bot.reply_to(message, f"*Here's some career advice based on your query:*\n\n{response}", parse_mode="Markdown")
        
    def resume_review_callback(call):
        logger.info(f"User {call.from_user.id} requested resume review")
        bot.answer_callback_query(call.id, "Opening Resume Review...")
        bot.send_message(call.message.chat.id, "*Please upload your resume as a PDF file, image, or document for review.*", parse_mode="Markdown")
        bot.register_next_step_handler(call.message, handle_resume_upload)

    def handle_resume_upload(message):
        try:
            logger.info(f"Starting resume processing for user {message.from_user.id}")
            extracted_text = ""
            
            # Handle document or image uploads
            if message.document:
                logger.info(f"Processing document for user {message.from_user.id}")
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                
                # Check if the document is a PDF
                if message.document.mime_type == "application/pdf":
                    pdf_stream = io.BytesIO(downloaded_file)
                    pdf_reader = PyPDF2.PdfReader(pdf_stream)
                    extracted_text = "\n".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
                else:
                    # Assume it's an image if not PDF
                    extracted_text = process_image(io.BytesIO(downloaded_file))
            
            elif message.photo:
                logger.info(f"Processing photo for user {message.from_user.id}")
                file_info = bot.get_file(message.photo[-1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                extracted_text = process_image(io.BytesIO(downloaded_file))
            
            else:
                bot.reply_to(message, "Please upload a PDF, image, or document.")
                return

            bot.reply_to(message, "Resume received! Reviewing...")

            logger.info(f"Extracted text from resume for user {message.from_user.id}: {extracted_text}")

            # Analyze the resume (mock service)
            analysis = process_image_and_text("Analyze this resume and provide feedback", extracted_text)

            # Compute ATS Score based on extracted resume text
            ats_score = calculate_ats_score(extracted_text)

            # Send the analysis and ATS score to the user
            bot.reply_to(message, f"*Resume Analysis:*\n\n{analysis}", parse_mode="Markdown")
            bot.reply_to(message, f"Your resume's ATS Score is: *{ats_score}/100*", parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Error processing resume upload: {str(e)}")
            bot.reply_to(message, "There was an error processing your resume. Please try again.")

    # Function to calculate a basic ATS score
    def calculate_ats_score(resume_text):
        """
        A more sophisticated ATS score calculation that includes checks for:
        - Key sections (like Work Experience, Skills, Education)
        - Keyword matching (frequency, relevance)
        - Penalties for missing sections or formatting issues
        """
        
        # Keywords for job-relevant skills, experience, etc.
        keywords = ['experience', 'skills', 'education', 'projects', 'certification']
        section_keywords = ['work experience', 'education', 'skills', 'projects']  # Critical sections
        
        total_keywords = len(keywords)
        total_sections = len(section_keywords)
        
        # Initialize score
        score = 0
        
        # Weightage for keywords (max 40 points)
        keyword_score = 0
        for keyword in keywords:
            if keyword.lower() in resume_text.lower():
                keyword_score += 1
        
        # Give a weightage of 40% for keywords (multiply by 2.5 to scale to 40 points)
        score += min(int((keyword_score / total_keywords) * 40), 40)
        
        # Weightage for presence of key sections (max 40 points)
        section_score = 0
        for section in section_keywords:
            if section.lower() in resume_text.lower():
                section_score += 1
        
        # Give a weightage of 40% for sections (multiply by 10 to scale to 40 points)
        score += min(int((section_score / total_sections) * 40), 40)
        
        # Penalty for missing key sections or overly long resume
        if section_score < total_sections:  # If some key sections are missing
            score -= 10
        
        # Bonus points for good formatting or keywords repeated in key sections (like experience)
        if resume_text.lower().count('experience') >= 2:
            score += 5  # Bonus for relevant content
        
        # Ensure score is within 0-100 range
        ats_score = max(0, min(score, 100))
        
        return ats_score


# Note: Make sure to call register_career_handler(bot) in your main bot loop or initialization code

    def sanitize_markdown(text):
        # Remove or escape problematic Markdown characters
        text = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)
        return text

    def extract_text_from_pdf(file_stream):
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_stream))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
