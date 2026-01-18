import json
import os
import sys
import time

# --- הגדרת נתיבים ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from services.embedding_service import get_text_embedding
from services.vector_store import VectorStore

INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'processed_news.json')

def load_data():
    print("🚀 Starting ingestion to ChromaDB...")
    
    # 1. אתחול המסד
    store = VectorStore()
    
    # 2. קריאת הנתונים
    if not os.path.exists(INPUT_FILE):
        print("❌ File not found!")
        return

    count = 0
    success_count = 0
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            count += 1
            try:
                article = json.loads(line)
                
                # בדיקה אם הכתבה כבר קיימת (אופציונלי, אבל חכם)
                # כרגע נסמוך על Chroma שיעדכן אם המזהה קיים
                
                # 3. הכנת הטקסט לחיפוש (Embedding)
                # אנחנו מחברים את כל המידע החשוב לטקסט אחד
                title = article.get('title', '')
                desc = article.get('description', '')
                summary = article.get('processing', {}).get('summary', '')
                
                # הטקסט המלא שייכנס לחיפוש
                combined_text = f"Title: {title}. Description: {desc}. Summary: {summary}"
                
                # יצירת הוקטור
                vector = get_text_embedding(combined_text)
                
                if vector:
                    # 4. הכנת המטא-דאטה (מידע נלווה לשליפה)
                    metadata = {
                        "source": article.get('source', {}).get('publisher', 'Unknown'),
                        "published_at": article.get('timestamps', {}).get('published_at', ''),
                        "sentiment": article.get('metadata', {}).get('sentiment', 'Neutral'),
                        "reliability": article.get('metadata', {}).get('reliability_score', 0.5)
                    }
                    
                    # 5. שמירה למסד
                    store.add_article(
                        article_id=article['article_id'],
                        text=combined_text, # שומרים את הטקסט כדי שנוכל לקרוא אותו בתוצאות
                        embedding=vector,
                        metadata=metadata
                    )
                    success_count += 1
                    print(f"✅ Added: {title[:30]}...")
                
                # השהייה קטנה כדי לא להפציץ את OpenAI (Rate Limit)
                time.sleep(0.2) 

            except Exception as e:
                print(f"⚠️ Failed line {count}: {e}")

    print(f"\n🏁 Finished! Loaded {success_count}/{count} articles into ChromaDB.")
    print(f"📊 Total documents in DB: {store.collection.count()}")

if __name__ == "__main__":
    load_data()