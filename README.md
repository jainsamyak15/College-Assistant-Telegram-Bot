# College Assistant Telegram Bot

The **College Assistant Telegram Bot** is a versatile tool designed to assist college students with academic, career-related tasks, and campus life management. This bot leverages natural language processing and document automation to provide valuable services such as assignment solving, career guidance, campus tips, and social connection opportunities.

## Table of Contents
- [Features](#features)
  - [Assignment Solver](#assignment-solver)
  - [Career Guide](#career-guide)
  - [Campus Life](#campus-life)
  - [Social Connect](#social-connect)
  - [Study Assistant](#study-assistant)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Steps](#steps)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

### Assignment Solver
- **Upload Assignments:** Students can upload their assignments as PDFs or images.
- **Automated Solutions:** The bot processes the uploaded documents and provides solutions or guidance based on the content.

### Career Guide
- **Resume Review:** Receive feedback on how to improve your resume.
- **Job Search:** Get tips and resources to aid in your job search.
- **Interview Tips:** Guidance on how to prepare for interviews and succeed in them.
- **Career Path Advice:** Get advice on choosing and navigating the right career path.
- **Salary Negotiation:** Strategies for negotiating a fair salary.
- **Cover Letter Generator:** Generate professional cover letters tailored to job positions.
- **Industry Insights:** Get insights on the current job market across different industries.
- **Mock Interviews:** Practice answering difficult interview questions and get feedback.

### Campus Life
- **Lost and Found:** Submit or search for lost and found items on campus.
- **Event Information:** Receive details about upcoming campus events and activities.

### Social Connect
- **Peer Mentorship Program:** Connect with mentors or mentees based on your field of study and interests.
- **Study Groups:** Find and join study groups for various subjects and courses.
- **Social Groups:** Join social groups to connect with peers who share similar interests.

### Study Assistant
- **Study Tips:** Get tips and resources to improve your study habits and performance.
- **Resource Recommendations:** Receive recommendations for books, articles, and other study materials relevant to your subjects.

## Technology Stack
- **Python**: The primary programming language used for building the bot.
- **Telegram Bot API**: Used to interact with Telegram and handle user messages and commands.
- **PyMuPDF**: For processing PDF documents.
- **Pillow**: For image processing.
- **PyPDF2**: For PDF manipulation.
- **pytesseract**: For Optical Character Recognition (OCR) on images.
- **reportlab**: For generating PDF documents.
- **requests**: For making HTTP requests.
- **dotenv**: For managing environment variables.
- **together**: Used for integrating with the Together API for additional services.

## Installation

### Prerequisites
Before you begin, ensure you have the following installed:
- **Python 3.11.7**
- **pip** (Python package installer)

### Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/college-assistant-bot.git
   cd college-assistant-bot
2. **Create and activate a virtual environment (optional but recommended)**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate

3. **Install the required packages:**:
    ```bash
    pip install -r requirements.txt

4. **Create a .env file in the root directory and add your Telegram Bot Token and Together API Key:**:
    ```bash
    TELEGRAM_API_TOKEN = 'your_telegram_bot_token'
    TOGETHER_API_KEY = 'your_together_api_key'


###Usage
1. **To run the bot, simply execute**:
  ```bash
  python main.py
