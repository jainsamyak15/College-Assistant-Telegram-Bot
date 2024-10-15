# File: college_assistant_bot/utils/helpers.py

import re
from typing import List, Dict
import json

def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing any potentially harmful characters.
    
    Args:
    text (str): The input text to sanitize.
    
    Returns:
    str: The sanitized text.
    """
    # Remove any HTML tags
    text = re.sub('<[^<]+?>', '', text)
    # Remove any special characters except alphanumeric, spaces, and basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()

def format_response(text: str, max_length: int = 4096) -> str:
    """
    Format the response to ensure it doesn't exceed Telegram's message length limit.
    
    Args:
    text (str): The response text to format.
    max_length (int): The maximum allowed length of the message.
    
    Returns:
    str: The formatted response text.
    """
    if len(text) <= max_length:
        return text
    
    # If the text is too long, truncate it and add an ellipsis
    return text[:max_length-3] + '...'

def create_menu_keyboard(options: List[Dict[str, str]]) -> List[List[Dict[str, str]]]:
    """
    Create a keyboard markup for Telegram bot menu.
    
    Args:
    options (List[Dict[str, str]]): A list of dictionaries containing 'text' and 'callback_data' for each button.
    
    Returns:
    List[List[Dict[str, str]]]: A nested list representing the keyboard markup.
    """
    return [[option] for option in options]

def load_json_data(file_path: str) -> Dict:
    """
    Load data from a JSON file.
    
    Args:
    file_path (str): The path to the JSON file.
    
    Returns:
    Dict: The loaded JSON data as a dictionary.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {file_path}")
        return {}

def save_json_data(data: Dict, file_path: str) -> None:
    """
    Save data to a JSON file.
    
    Args:
    data (Dict): The data to save.
    file_path (str): The path to the JSON file.
    """
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def extract_command(text: str) -> tuple:
    """
    Extract the command and the rest of the message from user input.
    
    Args:
    text (str): The user's message.
    
    Returns:
    tuple: (command, rest of the message)
    """
    parts = text.split(maxsplit=1)
    command = parts[0].lower().strip()
    message = parts[1] if len(parts) > 1 else ""
    return command, message

# Add more utility functions as needed
