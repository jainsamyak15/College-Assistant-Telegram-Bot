from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import logging


class GoogleSheetsLogger:
    def __init__(self, credentials_path, spreadsheet_id):
        """
        Initialize the Google Sheets logger

        Args:
            credentials_path (str): Path to the credentials.json file
            spreadsheet_id (str): ID of the Google Spreadsheet
        """
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.spreadsheet_id = spreadsheet_id

        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path, scopes=self.SCOPES
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            self.sheet = self.service.spreadsheets()
            logging.info("Successfully initialized Google Sheets logger")
        except Exception as e:
            logging.error(f"Error initializing Google Sheets logger: {str(e)}")
            raise

    def log_interaction(self, user_id, username, query_type, user_query, ai_response):
        """
        Log a user interaction to Google Sheets

        Args:
            user_id (str): Telegram user ID
            username (str): Telegram username
            query_type (str): Type of query (text, photo, document, etc.)
            user_query (str): User's question or input
            ai_response (str): AI's response
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = [
                timestamp,
                str(user_id),
                username or "N/A",
                query_type,
                user_query,
                ai_response
            ]

            request = self.sheet.values().append(
                spreadsheetId=self.spreadsheet_id,
                range='Sheet1!A:F',  # Assumes first sheet with headers
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [row]}
            )
            request.execute()
            logging.debug(f"Successfully logged interaction for user {user_id}")
        except Exception as e:
            logging.error(f"Error logging to Google Sheets: {str(e)}")
            raise