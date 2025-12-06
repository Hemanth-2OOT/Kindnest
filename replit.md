# KindNest

## Overview
KindNest is a cyberbullying detection tool that helps users check if messages contain harmful or toxic content. It's designed as a safe space for young people to analyze messages they receive.

**Current State**: Fully functional static web application running on Replit

## Project Type
- **Frontend**: Static HTML/CSS/JavaScript application
- **Backend**: None (client-side only)
- **Server**: Simple Python HTTP server for serving static files

## Features
- Text analysis for toxic content detection
- Keyword-based toxicity scoring system
- Screenshot upload with simulated OCR
- Email alert preview for trusted adults
- Emotional support messaging

## Project Structure
```
.
├── index.html       # Main application page
├── style.css        # Styling with Nunito font
├── script.js        # Client-side logic for toxicity detection
├── server.py        # Python HTTP server (serves static files on port 5000)
├── README.md        # Basic project readme
└── LICENSE          # Project license
```

## Technical Details
- **Port**: 5000 (frontend server)
- **Host**: 0.0.0.0 (allows Replit proxy access)
- **Caching**: Disabled via Cache-Control headers for development
- **Analysis**: Client-side keyword matching (simulated ML)

## Toxicity Detection
The application uses a keyword-based system with four severity levels:
- **80%+**: Threats, hate speech
- **60%+**: Bullying, harassment
- **40%+**: Body shaming, verbal abuse
- **20%+**: Unkind content

## Running the Application
The workflow "Start application" runs `python3 server.py` which:
1. Serves static files from the project directory
2. Listens on 0.0.0.0:5000
3. Disables caching for immediate updates

## Deployment Notes
- This is a static application suitable for static deployment
- No build process required
- All files served as-is
