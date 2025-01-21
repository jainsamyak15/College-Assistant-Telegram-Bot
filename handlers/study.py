import os
import PyPDF2
import logging
from io import BytesIO
from services.llama_vision import process_text
from services.flux_schnell import process_image
import time
from utils.google_sheets_logger import GoogleSheetsLogger
from dotenv import load_dotenv
# from config import GOOGLE_SHEETS_CREDENTIALS, GOOGLE_SHEETS_SPREADSHEET_ID

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
GOOGLE_SHEETS_SPREADSHEET_ID = '1CC0MvsG65IGV1rhRK6q2ORi0iiX93TX1Fk91V4ImO7Q'

load_dotenv()
GOOGLE_SHEETS_CREDENTIALS= os.getenv("GOOGLE_SHEETS_CREDENTIALS")
# Initialize sheets logger
sheets_logger = GoogleSheetsLogger(GOOGLE_SHEETS_CREDENTIALS, GOOGLE_SHEETS_SPREADSHEET_ID)

# Store user's document content
user_documents = {}


def register_study_handler(bot):
    @bot.callback_query_handler(func=lambda call: call.data == "study")
    def study_callback(call):
        logging.debug(f"Study callback triggered for user {call.message.chat.id}")
        bot.answer_callback_query(call.id, "Opening Study Assistant...")
        response = "*Study Assistant: Ask me any academic question or upload an image of your notes/textbook.*"
        bot.send_message(call.message.chat.id, response, parse_mode="Markdown")

        # Log interaction
        sheets_logger.log_interaction(
            call.message.chat.id,
            call.message.chat.username,
            "study_start",
            "Started study assistant",
            response
        )

    @bot.message_handler(
        func=lambda message: message.text and not message.text.startswith('/') and message.chat.id in user_documents)
    def handle_document_chat(message):
        logging.debug(f"Document chat handler triggered for user {message.chat.id}")
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            response = process_text(
                f"Based on the following document: {user_documents[message.chat.id]}\n\nUser question: {message.text}")
            send_long_message(bot, message.chat.id, response)

            # Log interaction
            sheets_logger.log_interaction(
                message.chat.id,
                message.chat.username,
                "document_chat",
                message.text,
                response
            )
        except Exception as e:
            logging.error(f"Error in handle_document_chat: {str(e)}")
            error_message = f"An unexpected error occurred: {str(e)}"
            bot.reply_to(message, error_message)

            # Log error
            sheets_logger.log_interaction(
                message.chat.id,
                message.chat.username,
                "document_chat_error",
                message.text,
                error_message
            )

    @bot.message_handler(func=lambda message: message.text and not message.text.startswith(
        '/') and message.chat.id not in user_documents)
    def handle_text(message):
        logging.debug(f"Text handler triggered for user {message.chat.id}")
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            response = process_text(message.text)
            send_long_message(bot, message.chat.id, response)

            # Log interaction
            sheets_logger.log_interaction(
                message.chat.id,
                message.chat.username,
                "text_chat",
                message.text,
                response
            )
        except Exception as e:
            logging.error(f"Error in handle_text: {str(e)}")
            error_message = f"An unexpected error occurred: {str(e)}"
            bot.reply_to(message, error_message)

            # Log error
            sheets_logger.log_interaction(
                message.chat.id,
                message.chat.username,
                "text_chat_error",
                message.text,
                error_message
            )

    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        logging.debug(f"Photo handler triggered for user {message.chat.id}")
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            response = process_image(downloaded_file)
            bot.reply_to(message, response)

            # Log interaction
            sheets_logger.log_interaction(
                message.chat.id,
                message.chat.username,
                "photo",
                "Image uploaded",
                response
            )
        except Exception as e:
            logging.error(f"Error in handle_photo: {str(e)}")
            error_message = f"An error occurred while processing the image: {str(e)}"
            bot.reply_to(message, error_message)

            # Log error
            sheets_logger.log_interaction(
                message.chat.id,
                message.chat.username,
                "photo_error",
                "Image upload failed",
                error_message
            )

    @bot.message_handler(content_types=['document'])
    def handle_document(message):
        logging.debug(f"Document handler triggered for user {message.chat.id}")
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            if message.document.mime_type == 'application/pdf':
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                pdf_text = extract_text_from_pdf(downloaded_file)

                user_documents[message.chat.id] = pdf_text

                response = "*I've read your document. You can now ask me questions about it. To exit document chat mode, type '/exit_doc_chat'.*"
                bot.reply_to(message, response, parse_mode="Markdown")

                # Log interaction
                sheets_logger.log_interaction(
                    message.chat.id,
                    message.chat.username,
                    "pdf_upload",
                    "PDF document uploaded",
                    response
                )
            else:
                response = "*Sorry, I can only process PDF files at the moment.*"
                bot.reply_to(message, response, parse_mode="Markdown")

                # Log interaction
                sheets_logger.log_interaction(
                    message.chat.id,
                    message.chat.username,
                    "invalid_document",
                    "Non-PDF document uploaded",
                    response
                )
        except Exception as e:
            logging.error(f"Error in handle_document: {str(e)}")
            error_message = f"*An error occurred while processing the PDF: {str(e)}*"
            bot.reply_to(message, error_message, parse_mode="Markdown")

            # Log error
            sheets_logger.log_interaction(
                message.chat.id,
                message.chat.username,
                "pdf_error",
                "PDF processing failed",
                error_message
            )
    @bot.message_handler(commands=['exit_doc_chat'])
    def exit_doc_chat(message):
        logging.debug(f"Exit document chat triggered for user {message.chat.id}")
        if message.chat.id in user_documents:
            del user_documents[message.chat.id]
            bot.reply_to(message, "Exited document chat mode. You can now ask general questions or upload a new document.")
        else:
            bot.reply_to(message, "You're not in document chat mode.")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def send_long_message(bot, chat_id, text):
    if len(text) <= 4096:
        bot.send_message(chat_id, text)
    else:
        parts = [text[i:i+4096] for i in range(0, len(text), 4096)]
        for part in parts:
            bot.send_message(chat_id, part)
            time.sleep(0.5)  # Add a small delay between messages