import os
import json
import sys
from openai import OpenAI
from dotenv import load_dotenv

# --- PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from prompts.news_analysis_prompt import SYSTEM_PROMPT

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
#----------------------

def analyze_article_with_ai(title, description, source_name):
    """
    פונקציה שמקבלת פרטי כתבה ומחזירה ניתוח חכם (JSON)
    עם סנטימנט, סיכום, ישויות וציון אמינות.
    """
    
    # אם אין מספיק מידע, נחזיר תשובה ריקה כדי לא לבזבז כסף
    if not title:
        return None

    # בניית הטקסט לניתוח - הוספנו את המקור בצורה ברורה יותר
    user_content = f"""
    Analyze this article:
    Title: {title}
    Source: {source_name}
    Description: {description}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT}, # שימוש בפרומפט החיצוני
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.0, # אפס יצירתיות - אנחנו רוצים דיוק
        )

        analysis_result = json.loads(response.choices[0].message.content)
        return analysis_result

    except Exception as e:
        print(f"⚠️ AI Analysis Failed: {e}")
        return None