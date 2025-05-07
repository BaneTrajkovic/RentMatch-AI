# RentMatch.AI - MVP Documentation

## Overview

RentMatch.AI is an innovative rental property platform that leverages AI to streamline the rental process for both landlords and renters. This MVP (Minimum Viable Product) showcases the core functionalities including property listings, AI-powered chats, application management, and AI-assisted lease negotiations.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation & Setup](#installation--setup)
3. [User Credentials](#user-credentials)
4. [Core Features](#core-features)
   - [Property Search](#property-search)
   - [AI Chatbot Assistant](#ai-chatbot-assistant)
   - [Property Applications](#property-applications)
   - [AI Lease Negotiation](#ai-lease-negotiation)
5. [User Flows](#user-flows)
   - [Renter Experience](#renter-experience)
   - [Landlord Experience](#landlord-experience)
6. [Technical Architecture](#technical-architecture)
7. [API Integrations](#api-integrations)
8. [Admin Commands](#admin-commands)
9. [Troubleshooting](#troubleshooting)

## System Requirements

- Python 3.13.3
- Django 5.2
- SQLite3 (already included)
- Redis (for WebSocket support)
- Google Gemini Pro API Key

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd RentMatch-AI-Project
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```
SECRET_KEY=your_django_secret_key
DEBUG=True
GEMINI_API_KEY=your_gemini_api_key
REDIS_URL=your_redis_url
```

### 4.1 Obtaining a Gemini API Key

**Option 1: Get your own Gemini API key**
1. Visit [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key) to create your API key
2. Copy your API key to the `constants.py.example` file
3. Rename the file to `constants.py`

**Option 2: Request an API key**
Email bt2639@columbia.edu to request a Gemini API key for this project.

### 5. Database Setup

The project includes a pre-configured SQLite3 database with sample data already loaded. No database migration or setup is required.

If you want to reset the database or start fresh, you can run:

```bash
python manage.py flush  # This will clear all data but keep the structure
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

## User Credentials

### Renter Access
- **Username**: `renterMVP`
- **Password**: `rentmatchMVP1`

### Landlord Access
- **Username**: `landlordMVP`
- **Password**: `landlordMVP`

## Core Features

### Property Search

The platform offers advanced property search capabilities:

- **Location-based search**: Find properties in specific neighborhoods or by address keywords
- **Filter by criteria**: Price range, number of bedrooms/bathrooms, amenities
- **Detailed property pages**: View images, features, floor plans, and neighborhood information
- **Save favorites**: Renters can save properties to revisit later

### AI Chatbot Assistant

Our general-purpose AI chatbot helps renters navigate the platform:

- **Natural conversation**: Engage in freeform discussions about rental needs and preferences
- **Property recommendations**: Ask the AI to suggest properties based on your requirements
- **Market information**: Get insights about NYC neighborhoods, rent ranges, and market trends
- **Personalized assistance**: The AI remembers your preferences throughout the conversation
- **Activate**: Access through the chat icon in the navigation bar

#### Chatbot Commands

The chatbot responds to natural language queries such as:
- "Find me a 2-bedroom apartment in Brooklyn under $3000"
- "What's the average rent in Manhattan?"
- "Tell me about the East Village neighborhood"

### Property Applications

The application system streamlines the rental application process:

- **One-click apply**: Renters can apply to properties with a single click
- **Application tracking**: View status of all submitted applications
- **Direct communication**: Message landlords about specific properties
- **Document management**: Upload and share required documentation

### AI Lease Negotiation

The AI-powered lease negotiation system is the core innovative feature:

- **Structured negotiations**: AI facilitates discussions between renters and landlords
- **Legal guidance**: Get information on lease terms, rights, and market standards
- **Term drafting**: AI can help draft clear, equitable lease terms
- **Digital signing**: Finalize leases digitally right in the platform
- **Contextual awareness**: AI tracks the entire conversation history to provide relevant responses

#### How to Use the AI Lease Assistant

1. In a property chat between landlord and renter, type `AI:` followed by your request
2. The AI will only respond when specifically prompted with the `AI:` prefix
3. Example: `AI: Can you help us draft a 12-month lease agreement?`
4. For lease finalization, both parties must type "Yes" followed by their full legal name

## User Flows

### Renter Experience

1. **Sign up/login**: Create an account or log in with test credentials
2. **Complete profile**: Add personal information, income verification, rental history
3. **Search properties**: Use filters or AI chat to find suitable properties
4. **Apply to properties**: Submit applications to properties of interest
5. **Negotiate lease**: Once approved by a landlord, use the AI-assisted negotiation
6. **Sign lease**: Finalize the agreement using the digital signature process

### Landlord Experience

1. **Login**: Use landlord credentials (landlordMVP/landlordMVP)
2. **Review applications**: See all applications submitted by interested renters
3. **Communicate with applicants**: Message renters directly about their applications
4. **Negotiate terms**: Use the AI-assisted platform to finalize lease details
5. **Finalize leases**: Complete the process with digital signatures

## Technical Architecture

RentMatch.AI is built on a modern tech stack:

- **Backend**: Django 5.2 (Python 3.13.3) with Django Channels for WebSockets
- **Database**: SQLite3 (pre-configured with sample data)
- **Real-time communication**: Redis + Django Channels
- **AI integration**: Google Gemini Pro API
- **Frontend**: Django templates with Bootstrap 5 and JavaScript

### Key Components

- **Users app**: Authentication, user profiles, and permissions
- **Negotiation app**: Property listings, applications, and lease negotiation
- **Chatbot app**: General-purpose AI assistance

## API Integrations

- **Google Gemini API**: Powers both the general chatbot and the lease negotiation assistant
- **Property Data API**: Sample property data based on NYC listings

## Admin Commands

### Manage Property Applications

Delete all property applications and messages (useful for testing):

```bash
python manage.py delete_all_applications
```

Use the `--dry-run` flag to preview what would be deleted:

```bash
python manage.py delete_all_applications --dry-run
```

### Load Sample Data

If you've reset the database and need to reload sample data:

```bash
python manage.py load_sample_properties
python manage.py create_test_users
```

## Troubleshooting

### WebSocket Connection Issues

If you experience connection issues with the chat functionality:

1. Ensure Redis is running
2. Verify Django Channels configuration in `settings.py`
3. Check browser console for WebSocket errors

### AI Assistant Not Responding

1. Verify your Gemini API key is correctly set
2. For negotiation assistant, ensure messages start with `AI:` 
3. Check server logs for any API rate limiting or errors

### Database Reset

If you need to reset the database to its original state:

```bash
# Make a backup of the original db.sqlite3 file first
cp db.sqlite3 db.sqlite3.backup

# Then you can either:
# 1. Restore from the original backup
cp db.sqlite3.backup db.sqlite3

# OR 2. Reset and recreate
python manage.py flush  # Clear all data
python manage.py create_test_users  # Recreate test users
python manage.py load_sample_properties  # Load sample properties
```

---

For technical support or questions, contact the development team.

© 2025 RentMatch.AI - All rights reserved 