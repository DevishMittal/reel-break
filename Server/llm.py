import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY is not set. Please add it to your .env file.")

client = Groq(api_key=GROQ_API_KEY)

def detect_short_form_video(ocr_text: str) -> dict:
    """
    Uses Groq to classify if the user is on a short-form video platform.
    Returns platform information or None if not detected.
    """
    prompt = f"""
    You are an AI classifier for detecting short-form video platforms from screen content.
    Analyze the given OCR text and determine if the user is currently on one of these platforms:
    
    **SHORT-FORM VIDEO PLATFORMS:**
    1. TikTok 
    2. Instagram Reels
    3. YouTube Shorts
    4. Snapchat
    5. Facebook Reels
    
    **DETECTION CRITERIA:**
    - TikTok: "For You", "Following", "@username", "TikTok", video duration counter, comments/likes UI
    - Instagram Reels: "Instagram", "Reels", "Instagram Reels", IG-specific UI elements, Instagram profile references
    - YouTube Shorts: "Shorts", "YouTube", YouTube-specific UI elements, subscriber counts
    - Snapchat: "Snapchat", Story indicators, message UI, camera interface elements, Snap-specific emojis
    - Facebook Reels: "Facebook", "FB", "Facebook Reels", Facebook-specific navigation, Facebook profile references

    **IMPORTANT DISTINCTIONS:**
    - Instagram Reels will typically contain Instagram-specific elements like "Instagram", profile links, or IG icons
    - Facebook Reels will contain Facebook-specific elements like "Facebook", FB logos, or Facebook-style notifications
    - If the text contains elements from both platforms but is primarily Instagram-oriented, classify as Instagram Reels
    
    **RESPONSE FORMAT:**
    Return a JSON object with these fields:
    1. "detected": true/false - whether any platform was detected
    2. "platform": the platform name or "none" (use exact platform names from the list above)
    3. "confidence": your confidence level (0.0-1.0)
    
    **OCR TEXT TO ANALYZE:**
    "{ocr_text}"
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200,
            response_format={"type": "json_object"}
        )

        result = response.choices[0].message.content
        return result

    except Exception as e:
        print(f"❌ Error classifying video platform: {e}")
        return {"detected": False, "platform": "none", "confidence": 0.0, "error": str(e)}


def generate_intervention_message(platform: str, usage_stats: dict) -> str:
    """
    Generates a personalized intervention message based on usage patterns.
    """
    prompt = f"""
    You are ScreenBreak, a digital wellbeing assistant that helps users be mindful of their 
    short-form video consumption. Create a friendly, non-judgmental intervention message
    based on the user's current usage statistics.
    
    **PLATFORM:** {platform}
    **TODAY'S USAGE:** {usage_stats.get('today_minutes', 0)} minutes
    **DAILY GOAL:** {usage_stats.get('daily_goal_minutes', 30)} minutes
    **CURRENT SESSION:** {usage_stats.get('current_session_minutes', 0)} minutes
    **TIMES OPENED TODAY:** {usage_stats.get('times_opened_today', 0)}
    
    Create a brief, encouraging message (max 2 sentences) that:
    1. Acknowledges their current usage in a non-judgmental way
    2. Gently suggests an alternative activity or reminds them of their goal
    3. Uses a supportive, friendly tone
    
    The message should be short enough to display as a notification.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100,
        )

        message = response.choices[0].message.content.strip()
        return message

    except Exception as e:
        print(f"❌ Error generating intervention message: {e}")
        return "You've been scrolling for a while. Maybe take a quick break?"