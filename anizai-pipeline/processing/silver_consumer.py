import json
import time
import os  # <--- הוספנו את זה (חובה בשביל עבודה עם נתיבים)
import sys
from datetime import datetime
from kafka import KafkaConsumer

# --- CONFIGURATION & PATH SETUP ---

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from services.ai_enrichment import analyze_article_with_ai

TOPIC_NAME = 'news_raw_data'
KAFKA_SERVER = 'localhost:9092'

# 2. הגדרת הנתיב המלא לקובץ הפלט: anizai-pipeline/data/processed/processed_news.json
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'processed_news.json')

# 3. וידוא שהתיקייה קיימת - אם לא, הקוד יוצר אותה אוטומטית
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# ----------------------------------

def clean_text(text):
    """Simple text cleaning function"""
    if not text:
        return ""
    return " ".join(text.split())

def process_message(message_value):
    # 1. בדיקות תקינות
    if message_value.get('title') == '[Removed]':
        return None
    if not message_value.get('title') or not message_value.get('url'):
        return None

    # --- חילוץ חכם של שם המקור (התיקון לקריסה) ---
    raw_source = message_value.get('source')
    source_name = 'Unknown'
    
    if isinstance(raw_source, dict):
        # אם זה מילון (כמו שציפינו), נחלץ את ה-name
        source_name = raw_source.get('name', 'Unknown')
    elif isinstance(raw_source, str):
        # אם זה סתם סטרינג, נשתמש בו כמו שהוא
        source_name = raw_source

# --- שלב ה-AI: קריאה למוח ---
    # אנחנו שולחים את הכותרת והתיאור לניתוח
    print(f"🤖 Analyzing with AI: {message_value['title'][:30]}...") # לוג כדי שתראה שזה עובד
    
    ai_result = analyze_article_with_ai(
        title=message_value.get('title'),
        description=message_value.get('description'),
        source_name=source_name # שימוש במשתנה שחילצנו בבטחה
    )
    
    # אם ה-AI נכשל, נשתמש בערכי ברירת מחדל ריקים
    if not ai_result:
        ai_result = {
            "sentiment": "Neutral",
            "confidence_level": 0.0,
            "summary": message_value.get('description'), # אם אין AI, התיאור הוא הסיכום
            "entities": [],
            "reliability_score": 0.5
        }


    # 2. בניית האובייקט לפי הסכמה של הפרויקט
    processed_article = {
        "article_id": str(abs(hash(message_value['url']))),
        
        "source": {
            "collector": "newsapi_scraper",
            "publisher": clean_text(source_name),
            "source_type": "news",
            "reliability_score": ai_result.get('reliability_score')
        },
        
        "author": {
            "name": clean_text(message_value.get('author')),
            "is_verified_expert": False
        },
        
        "url": message_value['url'],
        "language": "en",
        "title": clean_text(message_value['title']),
        "body": None,
        "description": clean_text(message_value.get('description')),
        
        "timestamps": {
            "published_at": message_value.get('publishedAt'),
            "collected_at": datetime.now().isoformat()
        },
        
        "metadata": {
            "sentiment": ai_result.get('sentiment'),
            "entities": ai_result.get('entities'),
            "confidence_level": ai_result.get('confidence_level')
        },
        
        "processing": {
            "summary": ai_result.get('summary'),
            "embedded": False,
            "summary_done": True
        }
    }
    
    return processed_article

def save_to_json_file(data):
    # כאן אנחנו משתמשים ב-OUTPUT_FILE שהגדרנו למעלה עם הנתיב החכם
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
        f.write('\n')

def run_silver_consumer():
    print(f"Starting Silver Layer Consumer...")
    print(f"Saving data to: {OUTPUT_FILE}") # הדפסה כדי שתראה איפה זה נשמר
    
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='silver-layer-ai-group-v1',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    count = 0
    try:
        for message in consumer:
            raw_data = message.value
            clean_data = process_message(raw_data)
            
            if clean_data:
                save_to_json_file(clean_data)
                count += 1
                print(f"✅ Saved article {count}: {clean_data['title'][:30]}... (Sentiment: {clean_data['metadata']['sentiment']})")
            
    except KeyboardInterrupt:
        print("\nStopping consumer...")
        consumer.close()

if __name__ == '__main__':
    run_silver_consumer()