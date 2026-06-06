import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"🔑 Gemini API Key loaded: {api_key[:10]}..." if api_key else "❌ Gemini API Key NOT found!")

if not api_key:
    raise Exception("GEMINI_API_KEY not found in .env file!")

genai.configure(api_key=api_key)

def analyze_emotion(description: str, category: str) -> str:
    if not description:
        return "neutral"
        
    prompt = f"""
    Analyze this expense for emotional or stress-driven spending.
    Category: {category}
    Description: {description}
    Reply with ONLY one of these words: 'stress', 'panic', 'joy', 'neutral'.
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text.strip().lower()
    except Exception as e:
        desc_lower = description.lower()
        stress_score = sum(3 for word in ["stress", "panic", "worried", "anxious", "emergency", "rent"] if word in desc_lower)
        joy_score = sum(3 for word in ["happy", "celebrate", "joy", "fun", "treat"] if word in desc_lower)
        if stress_score > joy_score and stress_score >= 2: return "stress"
        elif joy_score > stress_score and joy_score >= 2: return "joy"
        return "neutral"

def generate_survival_plan(income: float, survival: float, joy: float, buffer: float, threats: list, stress_events: int, language: str = "en"):
    """Generates a 4-week survival plan in the requested language."""
    
    lang_instruction = "Return the plan in English. All text must be in English."
    if language == "am":
        lang_instruction = "Return the plan in Amharic (አማርኛ). All text must be in Amharic. Use simple, empathetic Amharic that an Ethiopian household would understand."

    prompt = f"""
    You are SUKET, an AI Household Stress Stabilization Platform for Ethiopian families.
    A user is facing financial pressure. Here is their exact data:
    - Monthly Income: {income} ETB
    - Current Buckets: Survival: {survival} ETB, Joy: {joy} ETB, Buffer: {buffer} ETB
    - Forecasted Threats: {threats}
    - Recent Stress-Driven Purchases: {stress_events}

    Generate a 4-week adaptive survival plan. 
    {lang_instruction}
    
    CRITICAL: The "action" and "focus" and "budget_adjustment" fields MUST be in {language.upper() if language == "am" else "ENGLISH"}.
    
    Return ONLY a valid JSON array of 4 objects.
    Each object must have: "week" (int), "action" (string), "focus" (string), "budget_adjustment" (string).
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"): raw_text = raw_text[7:-3]
        elif raw_text.startswith("```"): raw_text = raw_text[3:-3]
        return json.loads(raw_text)
    except Exception as e:
        print(f"⚠️ AI Plan Generation Failed. Using translated fallback template.")
        # TRANSLATED FALLBACK TEMPLATE
        if language == "am":
            return [
                {"week": 1, "action": "ምግም እና አጋጋ", "focus": "ሁሉንም ወጪዎች በጥብቅ ተከታተል።", "budget_adjustment": f"የአኑ ማጠራሚያ {buffer} ብር ነው። ጠብቀው።"},
                {"week": 2, "action": "ጫና ንስ", "focus": f"አደጋዎችን ቅነሱ: {', '.join(threats)}.", "budget_adjustment": f"ከደስታ {min(500, joy)} ብር ወደ ማጠራቀሚያ ያዛው።"},
                {"week": 3, "action": "ለአደጋዎች ይዘጋጁ", "focus": "ሁሉንም አስፈጊ ያልሆኑ ወጪዎች ያቁሙ።", "budget_adjustment": "የደስታ ውላን ሙሉ በሙሉ ያቀዝቁ።"},
                {"week": 4, "action": "ማጠራቀሚያ ግም ይገን", "focus": "የፋይናንስ ደህንነት መረብ ወደነበረ ይመልሱ።", "budget_adjustment": "ሁሉንም ቁጠባዎች ወደ ማራቀሚያ ይመልሱ።"}
            ]
        else:
            return [
                {"week": 1, "action": "Assess & Stabilize", "focus": "Track all expenses strictly.", "budget_adjustment": f"Current Buffer is {buffer} ETB. Protect it."},
                {"week": 2, "action": "Reduce Pressure", "focus": f"Address threats: {', '.join(threats)}.", "budget_adjustment": f"Move {min(500, joy)} ETB from Joy to Buffer."},
                {"week": 3, "action": "Prepare for Threats", "focus": "Pause all non-essential spending.", "budget_adjustment": "Freeze Joy bucket completely."},
                {"week": 4, "action": "Rebuild Buffer", "focus": "Restore financial safety net.", "budget_adjustment": "Redirect all savings back to Buffer."}
            ]

def parse_voice_input(transcript: str, language: str = "auto") -> dict:
    language_instruction = "Detect the language automatically."
    if language == "am": language_instruction = "The text is in Amharic (አማርኛ)."
    elif language == "en": language_instruction = "The text is in English."
    
    prompt = f"""
    You are an expense parser for a financial app. {language_instruction}
    User said: "{transcript}"
    Extract the expense information and return ONLY a valid JSON object:
    - "amount" (number, the expense amount in ETB)
    - "category" (string: "food", "transport", "rent", "utilities", "health", "entertainment", "other")
    - "description" (string, brief description)
    - "emotion" (string: "neutral", "stress", "joy", "panic")
    Return ONLY the JSON object.
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"): raw_text = raw_text[7:-3]
        elif raw_text.startswith("```"): raw_text = raw_text[3:-3]
        return json.loads(raw_text)
    except Exception as e:
        import re
        amharic_to_digit = {"አንድ": "1", "ሁለት": "2", "ስት": "3", "አት": "4", "አምስት": "5", "ስስት": "6", "ሰባት": "7", "ስምንት": "8", "ጠኝ": "9", "ዜሮ": "0", "አስር": "10", "መቶ": "100", "ሺ": "1000", "ሺህ": "1000"}
        processed_transcript = transcript
        for am_word, digit in amharic_to_digit.items():
            processed_transcript = processed_transcript.replace(am_word, f" {digit} ")
        numbers = re.findall(r'\d+', processed_transcript)
        amount = 0
        if len(numbers) == 2: amount = int(numbers[0]) * int(numbers[1])
        elif len(numbers) == 1: amount = int(numbers[0])
        elif len(numbers) > 2: amount = int(max(numbers, key=int))

        transcript_lower = transcript.lower()
        category = "other"
        description = transcript
        if any(word in transcript_lower for word in ["transport", "taxi", "bus", "ride", "car", "fuel", "መጓዣ", "ታክ", "አውቶብስ"]): category = "transport"
        elif any(word in transcript_lower for word in ["food", "restaurant", "lunch", "dinner", "coffee", "meal", "ምግብ", "ቡና"]): category = "food"
        elif any(word in transcript_lower for word in ["rent", "house", "apartment", "ኪራይ", "ት"]): category = "rent"
        elif any(word in transcript_lower for word in ["health", "medical", "doctor", "pharmacy", "medicine", "hospital", "ጤና", "መሃኒት"]): category = "health"
        elif any(word in transcript_lower for word in ["water", "electric", "utility", "bill", "ውሃ", "ኤሌትክ"]): category = "utilities"
        
        emotion = "neutral"
        if any(word in transcript_lower for word in ["stress", "panic", "emergency", "urgent", "worried", "ርሃት"]): emotion = "stress"
        elif any(word in transcript_lower for word in ["happy", "joy", "celebrate", "fun", "ደስታ"]): emotion = "joy"
        
        return {"amount": amount, "category": category, "description": description, "emotion": emotion}
