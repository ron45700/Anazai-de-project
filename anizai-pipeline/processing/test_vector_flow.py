import json
import os
import sys

# --- הגדרת נתיבים (כדי שנוכל לייבא את התיקייה services) ---
# אנחנו עולים תיקייה אחת למעלה מ-processing כדי להגיע לתיקייה הראשית
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from services.embedding_service import get_text_embedding

INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'processed_news.json')

def test_single_article_embedding():
    print(f"📂 Reading from: {INPUT_FILE}...")
    
    # בדיקה שהקובץ קיים
    if not os.path.exists(INPUT_FILE):
        print("❌ Error: Processed data file not found!")
        return

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            # קריאת השורה הראשונה בלבד
            first_line = f.readline()
            
            if not first_line:
                print("⚠️ File is empty.")
                return

            article = json.loads(first_line)
            
            # 1. חילוץ המידע שמעניין אותנו לחיפוש
            # אנחנו מחברים את הכותרת, התיאור, והסיכום (אם יש) לטקסט אחד ארוך
            title = article.get('title', '')
            desc = article.get('description', '')
            summary = article.get('processing', {}).get('summary', '')
            
            combined_text = f"{title}. {desc} {summary}"
            
            print(f"\n📰 Found Article: {title[:50]}...")
            print(f"📝 Text to embed ({len(combined_text)} chars): '{combined_text[:60]}...'")

            # 2. שליחה ל-OpenAI ליצירת וקטור
            print("🚀 Sending to embedding model...")
            vector = get_text_embedding(combined_text)

            # 3. הצגת התוצאה
            if vector:
                print(f"\n✅ SUCCESS! Generated vector with {len(vector)} dimensions.")
                print(f"🔢 Sample data (first 5 numbers): {vector[:5]}")
            else:
                print("\n❌ Failed to generate vector.")

    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    test_single_article_embedding()