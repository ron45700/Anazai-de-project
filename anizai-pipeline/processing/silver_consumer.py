import json
import time
import os  # <--- הוספנו את זה (חובה בשביל עבודה עם נתיבים)
from datetime import datetime
from kafka import KafkaConsumer

# --- CONFIGURATION & PATH SETUP ---

TOPIC_NAME = 'news_raw_data'
KAFKA_SERVER = 'localhost:9092'

# 1. חישוב הנתיב לתיקייה הראשית (anizai-pipeline)
# אנחנו עולים שתי רמות למעלה: מקובץ זה -> לתיקיית processing -> לתיקייה הראשית
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. הגדרת הנתיב המלא לקובץ הפלט: anizai-pipeline/data/processed/processed_news.json
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'processed_news.json')

# 3. וידוא שהתיקייה קיימת - אם לא, הקוד יוצר אותה אוטומטית
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# ----------------------------------

def clean_text(text):
    """Simple text cleaning function"""
    if not text:
        return None
    return " ".join(text.split())

def process_message(message_value):
    # 1. בדיקות תקינות
    if message_value.get('title') == '[Removed]':
        return None
    if not message_value.get('title') or not message_value.get('url'):
        return None

    # 2. בניית האובייקט לפי הסכמה של הפרויקט
    processed_article = {
        "article_id": str(abs(hash(message_value['url']))),
        
        "source": {
            "collector": "newsapi_scraper",
            "publisher": clean_text(message_value['source']),
            "source_type": "news",
            "reliability_score": None
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
            "published_at": message_value['publishedAt'],
            "collected_at": datetime.now().isoformat()
        },
        
        "metadata": {
            "sentiment": None,
            "entities": [],
            "confidence_level": None
        },
        
        "processing": {
            "embedded": False,
            "summary_done": False
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
        group_id='silver-layer-group',
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
                if count % 5 == 0:
                    print(f"Processed {count} articles. Last: {clean_data['title'][:30]}...")
            
    except KeyboardInterrupt:
        print("\nStopping consumer...")
        consumer.close()

if __name__ == '__main__':
    run_silver_consumer()