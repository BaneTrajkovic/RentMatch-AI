# RentMatch AI Project

A Django-based social network application with AI-powered chatbot and negotiation features.

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/your-username/RentMatch-AI-Project.git
cd RentMatch-AI-Project
```

2. Set up a virtual environment (optional but recommended):
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your API keys:
```bash
# Copy the example file and replace with your actual API key
cp constants.py.example constants.py
# Then edit constants.py with your Gemini API key
```

5. Run the development server:
```bash
python manage.py runserver
```

6. Visit `http://127.0.0.1:8000/` in your browser.

## Features

- User authentication and profiles
- AI chatbot for property inquiries
- Negotiation system
- Django Channels for real-time communication

## Database

This repository includes the SQLite database with pre-loaded data for immediate use. No database migrations or setup required. 