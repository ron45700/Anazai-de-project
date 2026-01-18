import os
from openai import OpenAI
from dotenv import load_dotenv

# טעינת משתני סביבה
load_dotenv()

# אתחול הקליינט (משתמש באותו מפתח שכבר יש לך ב-.env)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_text_embedding(text):
    """
    מקבלת טקסט ומחזירה וקטור (רשימה של מספרים floats).
    משתמשת במודל text-embedding-3-small של OpenAI.
    """
    # ניקוי בסיסי: הסרת תווי שורה חדשה שיכולים לבלבל את המודל
    text = text.replace("\n", " ")
    
    try:
        response = client.embeddings.create(
            input=[text],
            model="text-embedding-3-small"
        )
        # שליפת הוקטור מתוך התשובה
        embedding_vector = response.data[0].embedding
        return embedding_vector
    
    except Exception as e:
        print(f"⚠️ Error generating embedding: {e}")
        return None

# --- בדיקה עצמית (רק אם מריצים את הקובץ ישירות) ---
if __name__ == "__main__":
    test_text = "Apple released a new iPhone today."
    vector = get_text_embedding(test_text)
    
    if vector:
        print(f"✅ Success! Vector length: {len(vector)}")
        print(f"Sample values: {vector[:5]}...") # נדפיס רק את ה-5 הראשונים
    else:
        print("❌ Failed to generate embedding.")