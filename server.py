import os
import json
import base64
import logging
from flask import Flask, request, jsonify, send_from_directory

from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Optional
import resend

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder='static')

client = None

def get_resend_credentials():
    hostname = os.environ.get("REPLIT_CONNECTORS_HOSTNAME")
    x_replit_token = None
    
    if os.environ.get("REPL_IDENTITY"):
        x_replit_token = "repl " + os.environ.get("REPL_IDENTITY")
    elif os.environ.get("WEB_REPL_RENEWAL"):
        x_replit_token = "depl " + os.environ.get("WEB_REPL_RENEWAL")
    
    if not x_replit_token or not hostname:
        return None, None
    
    try:
        import urllib.request
        req = urllib.request.Request(
            f"https://{hostname}/api/v2/connection?include_secrets=true&connector_names=resend",
            headers={
                "Accept": "application/json",
                "X_REPLIT_TOKEN": x_replit_token
            }
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            connection = data.get("items", [{}])[0]
            settings = connection.get("settings", {})
            return settings.get("api_key"), settings.get("from_email")
    except Exception as e:
        logging.error(f"Error getting Resend credentials: {e}")
        return None, None

def get_gemini_client():
    global client
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key and client is None:
        client = genai.Client(api_key=api_key)
    return client

class ToxicityAnalysis(BaseModel):
    toxicity_score: int
    explanation: str
    categories: List[str]
    emotional_support: str

def detect_image_mime_type(image_bytes: bytes) -> str:
    if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return "image/png"
    elif image_bytes[:2] == b'\xff\xd8':
        return "image/jpeg"
    elif image_bytes[:6] in (b'GIF87a', b'GIF89a'):
        return "image/gif"
    elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        return "image/webp"
    return "image/jpeg"

def analyze_content_with_gemini(text: str, image_base64: Optional[str] = None) -> dict:
    system_prompt = """You are KindNest, an AI-powered cyberbullying prevention and emotional support system.
    
Your role is to analyze messages for harmful content including:
- Bullying and harassment
- Hate speech and discrimination
- Threats and intimidation
- Body shaming and personal attacks
- Exclusion and social manipulation
- Emotional manipulation

For each message, provide:
1. toxicity_score: A number from 0-100 representing how harmful the content is
   - 0-20: Safe and kind
   - 21-40: Mildly concerning, possibly unkind
   - 41-60: Moderately toxic, contains harmful elements
   - 61-80: Highly toxic, clear bullying/harassment
   - 81-100: Severely toxic, threats or hate speech

2. explanation: A clear, age-appropriate explanation of why the message is harmful (or why it's safe). Be specific about what makes it problematic.

3. categories: List the types of harmful content detected (e.g., "bullying", "harassment", "threats", "hate speech", "body shaming", "exclusion", "manipulation"). Empty list if the message is safe.

4. emotional_support: A warm, supportive message for the person who received this content. If the content is harmful:
   - Validate their feelings
   - Remind them it's not their fault
   - Encourage them to talk to a trusted adult
   - Provide comfort and reassurance
   If the content is safe, provide positive reinforcement about healthy communication.

Respond ONLY with valid JSON in this exact format:
{
    "toxicity_score": <number 0-100>,
    "explanation": "<string>",
    "categories": ["<category1>", "<category2>"],
    "emotional_support": "<string>"
}"""

    contents = []
    
    if image_base64:
        try:
            image_bytes = base64.b64decode(image_base64)
            mime_type = detect_image_mime_type(image_bytes)
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
            contents.append("Analyze the text content shown in this screenshot for cyberbullying or harmful content.")
        except Exception as e:
            logging.error(f"Error processing image: {e}")
    
    if text:
        contents.append(f"Analyze this message for harmful content:\n\n\"{text}\"")
    
    if not contents:
        return {
            "toxicity_score": 0,
            "explanation": "No content provided to analyze.",
            "categories": [],
            "emotional_support": "Feel free to paste a message or upload a screenshot anytime you need help checking if something is kind."
        }

    gemini_client = get_gemini_client()
    if not gemini_client:
        logging.warning("Gemini API key not configured, using fallback analysis")
        return fallback_analysis(text or "")

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
            ),
        )
        
        raw_json = response.text
        logging.info(f"Gemini response: {raw_json}")
        
        if raw_json:
            data = json.loads(raw_json)
            return {
                "toxicity_score": min(100, max(0, int(data.get("toxicity_score", 0)))),
                "explanation": data.get("explanation", "Unable to analyze content."),
                "categories": data.get("categories", []),
                "emotional_support": data.get("emotional_support", "Remember, you deserve to be treated with kindness.")
            }
    except Exception as e:
        logging.error(f"Gemini analysis error: {e}")
        return fallback_analysis(text or "")
    
    return fallback_analysis(text or "")

def fallback_analysis(text: str) -> dict:
    keyword_sets = [
        {"level": 85, "keywords": ["kill", "die", "murder", "hurt you"], "categories": ["threats", "violence"]},
        {"level": 70, "keywords": ["hate", "disgusting", "worthless"], "categories": ["hate speech", "harassment"]},
        {"level": 55, "keywords": ["stupid", "idiot", "dumb", "loser", "nobody likes"], "categories": ["bullying", "harassment"]},
        {"level": 40, "keywords": ["ugly", "fat", "weird", "gross"], "categories": ["body shaming", "personal attacks"]},
        {"level": 25, "keywords": ["annoying", "boring", "lame"], "categories": ["unkind language"]}
    ]
    
    score = 0
    categories = set()
    lower_text = text.lower()
    
    for item in keyword_sets:
        for keyword in item["keywords"]:
            if keyword in lower_text:
                score = max(score, item["level"])
                for cat in item["categories"]:
                    categories.add(cat)
    
    if score >= 70:
        explanation = "This message contains highly toxic content that is meant to hurt and intimidate."
        support = "This message is not okay, and the things being said are not true. You are valuable and deserve respect. Please talk to a trusted adult about what you're experiencing. It's not your fault, and you don't have to face this alone."
    elif score >= 40:
        explanation = "This message contains hurtful language that could be considered bullying or harassment."
        support = "It's natural to feel upset when someone sends messages like this. Remember that hurtful words say more about the person saying them than about you. Consider talking to someone you trust about how this made you feel."
    elif score >= 20:
        explanation = "This message has some unkind elements that could be hurtful."
        support = "While this message isn't the kindest, try not to let it bring you down. You have the power to focus on the positive people in your life who appreciate you."
    else:
        explanation = "This message appears to be safe and doesn't contain harmful content."
        support = "This looks like a normal, friendly message! It's great to see positive communication. Keep surrounding yourself with people who treat you with kindness."
    
    return {
        "toxicity_score": score,
        "explanation": explanation,
        "categories": list(categories),
        "emotional_support": support
    }

def generate_email_report(result: dict, parent_email: str) -> tuple:
    categories_text = ", ".join(result["categories"]) if result["categories"] else "concerning content"
    
    email_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #e74c3c;">KindNest Alert - Support May Be Needed</h2>
            <hr style="margin: 1rem 0; border: none; border-top: 2px solid #e74c3c;">
            <p>Dear Trusted Adult,</p>
            <p>This is an automated alert from <strong>KindNest</strong>, an AI-powered cyberbullying prevention system.</p>
            <p>A message was analyzed and found to contain <strong style="color: #e74c3c;">{categories_text}</strong> with a toxicity score of <strong style="color: #e74c3c;">{result["toxicity_score"]}%</strong>.</p>
            <p><strong>What this means:</strong> {result["explanation"]}</p>
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0;"><strong>Recommended action:</strong> We encourage you to have a calm, supportive conversation with your child. The goal is to provide comfort and safety, not to punish or blame. Ask open-ended questions about how they're feeling and reassure them that they can come to you with any concerns.</p>
            </div>
            <p>Remember, experiencing cyberbullying can cause feelings of sadness, anxiety, or isolation. Your support can make a significant difference.</p>
            <p>With care,<br><strong>The KindNest Team</strong></p>
        </div>
        </body>
        </html>
    """
    
    api_key, from_email = get_resend_credentials()
    email_sent = False
    
    if api_key and from_email:
        try:
            resend.api_key = api_key
            email_response = resend.Emails.send({
                "from": from_email,
                "to": [parent_email],
                "subject": "KindNest Alert - Support May Be Needed",
                "html": email_html
            })
            logging.info(f"Email sent successfully to {parent_email}: {email_response}")
            email_sent = True
        except Exception as e:
            logging.error(f"Error sending email: {e}")
    else:
        logging.warning("Resend not configured, email not sent")
    
    preview_html = f"""
        <p><strong>To:</strong> {parent_email}</p>
        <p><strong>Subject:</strong> KindNest Alert - Support May Be Needed</p>
        <hr style="margin: 1rem 0; border: none; border-top: 1px solid #ddd;">
        <p>Dear Trusted Adult,</p>
        <p>This is an automated alert from KindNest, an AI-powered cyberbullying prevention system.</p>
        <p>A message was analyzed and found to contain <strong>{categories_text}</strong> with a toxicity score of <strong>{result["toxicity_score"]}%</strong>.</p>
        <p><strong>What this means:</strong> {result["explanation"]}</p>
        <p><strong>Recommended action:</strong> We encourage you to have a calm, supportive conversation with your child.</p>
        <p>With care,<br>The KindNest Team</p>
    """
    
    return preview_html, email_sent

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')
    image_base64 = data.get('image_base64')
    parent_email = data.get('parent_email', '')
    
    result = analyze_content_with_gemini(text, image_base64)
    
    email_sent = False
    email_preview = None
    
    if result["toxicity_score"] >= 40 and parent_email:
        email_preview, email_sent = generate_email_report(result, parent_email)
    
    return jsonify({
        "toxicity_score": result["toxicity_score"],
        "explanation": result["explanation"],
        "categories": result["categories"],
        "emotional_support": result["emotional_support"],
        "email_sent": email_sent,
        "email_preview": email_preview
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
