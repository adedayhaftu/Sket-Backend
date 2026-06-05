import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"🔑 Gemini API Key loaded: {api_key[:10]}..." if api_key else "❌ Gemini API Key NOT found!")

if not api_key:
    raise Exception("GEMINI_API_KEY not found in .env file!")

# Initialize the Google GenAI client
client = genai.Client(api_key=api_key)

def analyze_emotion(description: str, category: str) -> str:
    """Uses AI to detect emotional spending, with a smart fallback if quota is hit."""
    if not description:
        return "neutral"
        
    prompt = f"""
    Analyze this expense for emotional or stress-driven spending.
    Category: {category}
    Description: {description}
    
    Reply with ONLY one of these words: 'stress', 'panic', 'joy', 'neutral'.
    """
    
    # 1. Try the Real Gemini AI
    try:
        print(f"🤖 Sending to AI: {description}")
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        emotion = response.text.strip().lower()
        print(f"🎭 Real AI Response: {emotion}")
        return emotion
        
    except Exception as e:
        # 2. HACKATHON FALLBACK: Heuristic Scoring Engine
        print(f"⚠️ AI Quota Hit. Activating Heuristic Fallback Engine.")
        desc_lower = description.lower()
        
        # Define weighted stress and joy indicators
        stress_keywords = {
            "stress": 3, "panic": 4, "worried": 2, "anxious": 3, 
            "scared": 3, "emergency": 4, "rent": 2, "inflation": 3, 
            "shock": 3, "debt": 3, "overdue": 2
        }
        joy_keywords = {
            "happy": 3, "celebrate": 3, "joy": 3, "fun": 2, 
            "treat": 2, "reward": 2, "gift": 2
        }
        
        stress_score = sum(weight for word, weight in stress_keywords.items() if word in desc_lower)
        joy_score = sum(weight for word, weight in joy_keywords.items() if word in desc_lower)
        
        # Determine emotion based on weighted scores
        if stress_score > joy_score and stress_score >= 2:
            emotion = "stress" if stress_score < 6 else "panic"
        elif joy_score > stress_score and joy_score >= 2:
            emotion = "joy"
        else:
            emotion = "neutral"
            
        print(f"🎭 Heuristic Engine Response: {emotion} (Stress Score: {stress_score}, Joy Score: {joy_score})")
        return emotion


def generate_survival_plan(income: float, survival: float, joy: float, buffer: float, threats: list, stress_events: int):
    """Uses AI to generate a completely unique 4-week survival plan based on exact data."""
    
    prompt = f"""
    You are SUKET, an AI Household Stress Stabilization Platform.
    A user is facing financial pressure. Here is their exact data:
    - Monthly Income: {income} ETB
    - Current Buckets: Survival: {survival} ETB, Joy: {joy} ETB, Buffer: {buffer} ETB
    - Forecasted Threats: {threats}
    - Recent Stress-Driven Purchases: {stress_events}

    Generate a 4-week adaptive survival plan to help them recover. 
    Return ONLY a valid JSON array of 4 objects. Do not write any text outside the JSON.
    Each object must have these exact keys: 
    "week" (integer 1-4), 
    "action" (string, short title), 
    "focus" (string, what they should do), 
    "budget_adjustment" (string, specific math on how to move money between Survival, Joy, and Buffer).

    Example format:
    [
      {{"week": 1, "action": "Stabilize", "focus": "Track every penny", "budget_adjustment": "Move 500 ETB from Joy to Buffer"}},
      {{"week": 2, "action": "Cut Costs", "focus": "Stop all eating out", "budget_adjustment": "Freeze Joy bucket at 0"}},
      {{"week": 3, "action": "Prepare", "focus": "Save for upcoming threat", "budget_adjustment": "Reallocate 10% of Survival to Buffer"}},
      {{"week": 4, "action": "Rebuild", "focus": "Restore normalcy", "budget_adjustment": "Gradually restore Joy spending"}}
    ]
    """
    
    try:
        print(f"🧠 Generating dynamic survival plan via AI...")
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        # Clean up the response to ensure it's pure JSON
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3]
            
        plan = json.loads(raw_text)
        print(f"✅ AI generated a unique {len(plan)}-week plan.")
        return plan
        
    except Exception as e:
        print(f"⚠️ AI Plan Generation Failed. Using dynamic fallback template.")
        # Fallback template if AI is down, but still uses their specific numbers
        return [
            {"week": 1, "action": "Assess & Stabilize", "focus": "Track all expenses strictly.", "budget_adjustment": f"Current Buffer is {buffer} ETB. Protect it."},
            {"week": 2, "action": "Reduce Pressure", "focus": f"Address threats: {', '.join(threats)}.", "budget_adjustment": f"Move {min(500, joy)} ETB from Joy to Buffer."},
            {"week": 3, "action": "Prepare for Threats", "focus": "Pause all non-essential spending.", "budget_adjustment": "Freeze Joy bucket completely."},
            {"week": 4, "action": "Rebuild Buffer", "focus": "Restore financial safety net.", "budget_adjustment": "Redirect all savings back to Buffer."}
        ]

def parse_voice_input(transcript: str, language: str = "auto") -> dict:
    """
    Uses AI to parse voice input in ANY language (English, Amharic, etc.)
    Returns structured expense data without any hardcoding.
    """
    
    language_instruction = ""
    if language == "am":
        language_instruction = "The text is in Amharic (አማርኛ)."
    elif language == "en":
        language_instruction = "The text is in English."
    else:
        language_instruction = "Detect the language automatically."
    
    prompt = f"""
    You are an expense parser for a financial app.
    {language_instruction}
    
    User said: "{transcript}"
    
    Extract the expense information and return ONLY a valid JSON object with these exact keys:
    - "amount" (number, the expense amount in ETB)
    - "category" (string, one of: "food", "transport", "rent", "utilities", "health", "entertainment", "other")
    - "description" (string, brief description of the expense)
    - "emotion" (string, one of: "neutral", "stress", "joy", "panic")
    
    If you cannot extract an amount, return amount as 0.
    If the text is unclear, make your best guess based on context.
    
    Return ONLY the JSON object, no other text.
    
    Example responses:
    {{"amount": 300, "category": "transport", "description": "Taxi ride home", "emotion": "neutral"}}
    {{"amount": 1500, "category": "health", "description": "Pharmacy for toothache", "emotion": "stress"}}
    """
    
    try:
        print(f"🎤 Parsing voice input via AI: {transcript}")
        response = client.models.generate_content(
            model="gemini-1.5-flash",  # Use the same model as other functions
            contents=prompt
        )
        
        # Clean up response
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3]
        
        parsed = json.loads(raw_text)
        print(f"✅ AI parsed voice: {parsed}")
        return parsed
        
    except Exception as e:
        print(f"⚠️ Voice parsing failed: {e}")
        print("🔄 Using smart fallback parser...")
        
        # SMART FALLBACK: Extract numbers and keywords without AI
        import re
        
        # Extract numbers from transcript
        numbers = re.findall(r'\d+', transcript)
        amount = int(numbers[0]) if numbers else 0
        
        # Determine category from keywords
        transcript_lower = transcript.lower()
        category = "other"
        description = transcript
        
        # Transport keywords
        if any(word in transcript_lower for word in ["transport", "taxi", "bus", "ride", "car", "fuel", "መጓጓዣ", "ታክሲ", "አውቶብስ"]):
            category = "transport"
            description = "Transport expense"
        # Food keywords
        elif any(word in transcript_lower for word in ["food", "restaurant", "lunch", "dinner", "coffee", "meal", "ምግብ", "ቡና", "ሬስቶራንት"]):
            category = "food"
            description = "Food expense"
        # Rent keywords
        elif any(word in transcript_lower for word in ["rent", "house", "apartment", "ኪራይ", "ቤት"]):
            category = "rent"
            description = "Rent payment"
        # Health keywords
        elif any(word in transcript_lower for word in ["health", "medical", "doctor", "pharmacy", "medicine", "hospital", "ጤና", "መድሃኒት", "ሆስፒታል"]):
            category = "health"
            description = "Medical expense"
        # Utilities keywords
        elif any(word in transcript_lower for word in ["water", "electric", "utility", "bill", "ውሃ", "ኤሌትሪክ"]):
            category = "utilities"
            description = "Utility bill"
        
        # Determine emotion
        emotion = "neutral"
        if any(word in transcript_lower for word in ["stress", "panic", "emergency", "urgent", "worried"]):
            emotion = "stress"
        elif any(word in transcript_lower for word in ["happy", "joy", "celebrate", "fun"]):
            emotion = "joy"
        
        fallback_result = {
            "amount": amount,
            "category": category,
            "description": description,
            "emotion": emotion
        }
        
        print(f"✅ Fallback parsed: {fallback_result}")
        return fallback_result