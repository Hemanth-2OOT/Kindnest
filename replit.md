# KindNest

## Overview
KindNest is an AI-powered cyberbullying prevention and emotional support system designed to make online communication safer, especially for students and teenagers. Users can paste or upload messages/screenshots from any platform, and the AI analyzes content for toxicity, harassment, hate speech, threats, and emotional harm.

**Current State**: Fully functional web application with Gemini AI integration

## Features
1. **Toxicity Analysis**: AI-powered detection with 0-100% scoring using Gemini 2.5 Flash
2. **Emotional Support**: Personalized comfort messages for recipients
3. **Parent Alert**: Automatic email sending via Resend to trusted adults when harmful content detected (toxicity >= 40%)
4. **Screenshot Analysis**: Upload images for text extraction and analysis
5. **Fallback System**: Keyword-based analysis when AI is unavailable

## Project Type
- **Frontend**: HTML/CSS/JavaScript
- **Backend**: Python Flask API
- **AI**: Google Gemini 2.5 Flash for content analysis

## Project Structure
```
.
├── index.html           # Main application page
├── static/
│   ├── style.css        # Modern UI styling
│   └── script.js        # Frontend logic and API calls
├── server.py            # Flask backend with Gemini integration
├── replit.md            # Project documentation
├── README.md            # Basic readme
└── LICENSE              # Project license
```

## Technical Details
- **Port**: 5000 (Flask server)
- **Host**: 0.0.0.0 (allows Replit proxy access)
- **AI Model**: Gemini 2.5 Flash
- **Fallback**: Keyword-based toxicity detection

## Environment Variables
- `GEMINI_API_KEY`: Required for AI-powered analysis (falls back to keyword analysis if not set)

## Toxicity Levels
- **0-20%**: Safe and kind
- **21-40%**: Mildly concerning
- **41-60%**: Moderately toxic
- **61-80%**: Highly toxic
- **81-100%**: Severely toxic (threats/hate speech)

## API Endpoints
- `GET /`: Serves the main application
- `GET /static/<file>`: Serves static assets
- `POST /api/analyze`: Analyzes text/images for toxicity

## Running the Application
The workflow "Start application" runs `python3 server.py` which:
1. Starts Flask on 0.0.0.0:5000
2. Serves the frontend UI
3. Processes analysis requests via Gemini AI

## Deployment
- Configured for autoscale deployment using gunicorn
- Production command: `gunicorn --bind=0.0.0.0:5000 server:app`
