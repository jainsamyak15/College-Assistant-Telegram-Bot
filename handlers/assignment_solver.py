import os
import logging
import fitz
import re
from io import BytesIO
from PIL import Image
import pytesseract
from telebot import TeleBot
from telebot.types import Message
from services.llama_vision import process_text
from utils.helpers import sanitize_input, format_response
from services.document_generator import generate_document
from config import UPLOAD_FOLDER


# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# User state dictionary
user_states = {}

def register_assignment_solver_handler(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: call.data == "assignment_solver")
    def assignment_solver_callback(call):
        logger.debug(f"Assignment solver callback triggered for user {call.message.chat.id}")
        user_states[call.message.chat.id] = "assignment_solver"
        bot.answer_callback_query(call.id, "Opening Assignment Solver...")
        bot.send_message(call.message.chat.id, "Welcome to the Assignment Solver! Please upload your assignment as a PDF or image.")

    @bot.message_handler(content_types=['document', 'photo'], func=lambda message: user_states.get(message.chat.id) == "assignment_solver")
    def handle_assignment(message: Message):
        logger.debug(f"Assignment handler triggered for user {message.chat.id}")
        try:
            if message.document:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                file_name = message.document.file_name
                assignment_text = extract_text_from_pdf(downloaded_file)
            elif message.photo:
                file_info = bot.get_file(message.photo[-1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                file_name = f"assignment_{message.photo[-1].file_id}.jpg"
                assignment_text = extract_text_from_image(downloaded_file)
            else:
                bot.reply_to(message, "Please upload a valid document or photo.")
                return

            logger.debug(f"Extracted text: {assignment_text[:500]}...")  # Log the first 500 characters

            bot.reply_to(message, "Assignment received! Processing...")

            # Process the assignment
            questions = extract_questions(assignment_text)
            logger.debug(f"Extracted questions: {questions}")

            if not questions:
                logger.warning("No questions extracted. Using fallback method.")
                questions = [{"question": "Please provide a summary of the main points in the assignment.", "marks": "N/A", "co": "N/A", "lo": "N/A"}]

            answers = generate_answers(questions)
            logger.debug(f"Generated answers: {answers[:2]}")  # Log the first two answers

            # Format the response
            formatted_response = format_assignment_solution(questions, answers)
            logger.debug(f"Formatted response: {formatted_response[:500]}...")  # Log the first 500 characters

            # Generate document with answers
            output_path = generate_document(formatted_response)
            logger.debug(f"Document generated at: {output_path}")

            # Check if the file exists and is not empty
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                # Send the document back to the user
                with open(output_path, 'rb') as doc:
                    bot.send_document(message.chat.id, doc, caption="Here's your solved assignment!")
            else:
                logger.error(f"Generated PDF is empty or does not exist: {output_path}")
                bot.reply_to(message, "An error occurred while generating the document. Please try again.")

            # Cleanup
            if os.path.exists(output_path):
                os.remove(output_path)

            # Reset user state
            user_states.pop(message.chat.id, None)

        except Exception as e:
            logger.error(f"Error in handle_assignment: {str(e)}", exc_info=True)
            bot.reply_to(message, f"An error occurred while processing your assignment: {str(e)}")

    @bot.message_handler(func=lambda message: message.text and message.text.lower().startswith('assignment:') and user_states.get(message.chat.id) == "assignment_solver")
    def handle_assignment_query(message):
        logger.debug(f"Assignment query handler triggered for user {message.chat.id}")
        query = sanitize_input(message.text[11:].strip())  # Remove 'assignment:' prefix
        response = process_text(f"Answer this assignment question: {query}")
        bot.reply_to(message, format_response(response))

        # Reset user state
        user_states.pop(message.chat.id, None)

# Function to extract text from PDF using PyMuPDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = fitz.open(stream=BytesIO(pdf_file), filetype="pdf")
    text = ""
    for page_num in range(len(pdf_reader)):
        page = pdf_reader.load_page(page_num)
        text += page.get_text("text")  # Extract text from page
    pdf_reader.close()
    logger.debug(f"Extracted text from PDF: {text[:500]}...")  # Log the first 500 characters
    return text

# Function to extract text from image using pytesseract
def extract_text_from_image(image_file):
    image = Image.open(BytesIO(image_file))
    text = pytesseract.image_to_string(image)
    logger.debug(f"Extracted text from image: {text[:500]}...")  # Log the first 500 characters
    return text

def extract_questions(text):
    # Use regex to find questions in the text
    question_pattern = r'(\d+)\s+(.*?)\s+(\d+)\s+(CO\d+)\s+(L\d+(?:,L\d+)*)'
    questions = re.findall(question_pattern, text, re.DOTALL)
    
    formatted_questions = []
    for q in questions:
        formatted_questions.append({
            "question": q[1].strip(),
            "marks": q[2],
            "co": q[3],
            "lo": q[4]
        })
    
    logger.debug(f"Extracted questions: {formatted_questions}")
    return formatted_questions

def generate_answers(questions):
    answers = []
    for q in questions:
        prompt = f"Provide a concise, accurate, and straightforward answer to this question: {q['question']} (CO: {q['co']}, LO: {q['lo']})"
        answer = process_text(prompt)
        answers.append(answer)
    logger.debug(f"Generated answers: {answers[:2]}")  # Log the first two answers
    return answers

def format_assignment_solution(questions, answers):
    formatted_solution = ""
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        formatted_solution += f"Question {i}: {q['question']}\n"
        formatted_solution += f"Marks: {q['marks']}, CO: {q['co']}, LO: {q['lo']}\n\n"
        formatted_solution += f"Answer: {a}\n\n"
        formatted_solution += "-" * 40 + "\n\n"
    logger.debug(f"Formatted solution: {formatted_solution[:500]}...")  # Log the first 500 characters
    return formatted_solution


# import os
# import logging
# import PyPDF2
# import re
# from io import BytesIO
# from PIL import Image
# import pytesseract
# from telebot import TeleBot
# from telebot.types import Message
# from services.llama_vision import process_text
# from utils.helpers import sanitize_input, format_response
# from services.document_generator import generate_document
# from config import UPLOAD_FOLDER

# # Set up logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # User state dictionary
# user_states = {}

# def register_assignment_solver_handler(bot: TeleBot):
#     @bot.callback_query_handler(func=lambda call: call.data == "assignment_solver")
#     def assignment_solver_callback(call):
#         logger.debug(f"Assignment solver callback triggered for user {call.message.chat.id}")
#         user_states[call.message.chat.id] = "assignment_solver"
#         bot.answer_callback_query(call.id, "Opening Assignment Solver...")
#         bot.send_message(call.message.chat.id, "Welcome to the Assignment Solver! Please upload your assignment as a PDF or image.")

#     @bot.message_handler(content_types=['document', 'photo'], func=lambda message: user_states.get(message.chat.id) == "assignment_solver")
#     def handle_assignment(message: Message):
#         logger.debug(f"Assignment handler triggered for user {message.chat.id}")
#         try:
#             if message.document:
#                 file_info = bot.get_file(message.document.file_id)
#                 downloaded_file = bot.download_file(file_info.file_path)
#                 file_name = message.document.file_name
#                 assignment_text = extract_text_from_pdf(downloaded_file)
#             elif message.photo:
#                 file_info = bot.get_file(message.photo[-1].file_id)
#                 downloaded_file = bot.download_file(file_info.file_path)
#                 file_name = f"assignment_{message.photo[-1].file_id}.jpg"
#                 assignment_text = extract_text_from_image(downloaded_file)
#             else:
#                 bot.reply_to(message, "Please upload a valid document or photo.")
#                 return

#             logger.debug(f"Extracted text: {assignment_text[:500]}...")  # Log the first 500 characters

#             bot.reply_to(message, "Assignment received! Processing...")

#             # Process the assignment
#             questions = extract_questions(assignment_text)
#             logger.debug(f"Extracted questions: {questions}")

#             if not questions:
#                 logger.warning("No questions extracted. Using fallback method.")
#                 questions = [{"question": "Please provide a summary of the main points in the assignment.", "marks": "N/A", "co": "N/A", "lo": "N/A"}]

#             answers = generate_answers(questions)
#             logger.debug(f"Generated answers: {answers[:2]}")  # Log the first two answers

#             # Format the response
#             formatted_response = format_assignment_solution(questions, answers)
#             logger.debug(f"Formatted response: {formatted_response[:500]}...")  # Log the first 500 characters

#             # Generate document with answers
#             output_path = generate_document(formatted_response)
#             logger.debug(f"Document generated at: {output_path}")

#             # Check if the file exists and is not empty
#             if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
#                 # Send the document back to the user
#                 with open(output_path, 'rb') as doc:
#                     bot.send_document(message.chat.id, doc, caption="Here's your solved assignment!")
#             else:
#                 logger.error(f"Generated PDF is empty or does not exist: {output_path}")
#                 bot.reply_to(message, "An error occurred while generating the document. Please try again.")

#             # Cleanup
#             if os.path.exists(output_path):
#                 os.remove(output_path)

#             # Reset user state
#             user_states.pop(message.chat.id, None)

#         except Exception as e:
#             logger.error(f"Error in handle_assignment: {str(e)}", exc_info=True)
#             bot.reply_to(message, f"An error occurred while processing your assignment: {str(e)}")

#     @bot.message_handler(func=lambda message: message.text and message.text.lower().startswith('assignment:') and user_states.get(message.chat.id) == "assignment_solver")
#     def handle_assignment_query(message):
#         logger.debug(f"Assignment query handler triggered for user {message.chat.id}")
#         query = sanitize_input(message.text[11:].strip())  # Remove 'assignment:' prefix
#         response = process_text(f"Answer this assignment question: {query}")
#         bot.reply_to(message, format_response(response))

#         # Reset user state
#         user_states.pop(message.chat.id, None)

# def extract_text_from_pdf(pdf_file):
#     pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file))
#     text = ""
#     for page in pdf_reader.pages:
#         text += page.extract_text() + "\n"
#     logger.debug(f"Extracted text from PDF: {text[:500]}...")  # Log the first 500 characters
#     return text

# def extract_text_from_image(image_file):
#     image = Image.open(BytesIO(image_file))
#     text = pytesseract.image_to_string(image)
#     logger.debug(f"Extracted text from image: {text[:500]}...")  # Log the first 500 characters
#     return text

# def extract_questions(text):
#     # Use regex to find questions in the text
#     question_pattern = r'(\d+)\s+(.*?)\s+(\d+)\s+(CO\d+)\s+(L\d+(?:,L\d+)*)'
#     questions = re.findall(question_pattern, text, re.DOTALL)
    
#     formatted_questions = []
#     for q in questions:
#         formatted_questions.append({
#             "question": q[1].strip(),
#             "marks": q[2],
#             "co": q[3],
#             "lo": q[4]
#         })
    
#     logger.debug(f"Extracted questions: {formatted_questions}")
#     return formatted_questions

# def generate_answers(questions):
#     answers = []
#     for q in questions:
#         prompt = f"Provide a concise, accurate, and straightforward answer to this question: {q['question']} (CO: {q['co']}, LO: {q['lo']})"
#         answer = process_text(prompt)
#         answers.append(answer)
#     logger.debug(f"Generated answers: {answers[:2]}")  # Log the first two answers
#     return answers

# def format_assignment_solution(questions, answers):
#     formatted_solution = ""
#     for i, (q, a) in enumerate(zip(questions, answers), 1):
#         formatted_solution += f"Question {i}: {q['question']}\n"
#         formatted_solution += f"Marks: {q['marks']}, CO: {q['co']}, LO: {q['lo']}\n\n"
#         formatted_solution += f"Answer: {a}\n\n"
#         formatted_solution += "-" * 40 + "\n\n"
#     logger.debug(f"Formatted solution: {formatted_solution[:500]}...")  # Log the first 500 characters
#     return formatted_solution