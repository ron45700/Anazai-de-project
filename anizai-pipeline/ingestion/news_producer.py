import json
import time
import requests
import os
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

# 1. Configuration
API_KEY = os.getenv('NEWS_API_KEY')
TOPIC_NAME = 'news_raw_data'
KAFKA_SERVER = 'localhost:9092'

if not API_KEY:
    raise ValueError("No API Key found! Please check your .env file.")
    
# Categories we want to fetch (these will act as our Keys)
CATEGORIES = ['sports', 'technology', 'business']

def fetch_news(category):
    """
    Fetches top headlines for a specific category from NewsAPI.
    """
    url = f'https://newsapi.org/v2/top-headlines?category={category}&language=en&apiKey={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('articles', [])
    else:
        print(f"Error fetching {category}: {response.status_code}")
        return []

def run_producer():
    print("Connecting to Kafka...")
    
    # Initialize the Producer
    # note: api_version is set to ensure compatibility with newer Kafka images
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'), # Auto-convert JSON to bytes
        key_serializer=lambda k: k.encode('utf-8'),               # Auto-convert String Key to bytes
        api_version=(2, 0, 2) 
    )

    print(f"Start fetching and sending news to topic '{TOPIC_NAME}'...")

    for category in CATEGORIES:
        articles = fetch_news(category)
        print(f"\n--- Processing Category: {category} ({len(articles)} articles) ---")
        
        for article in articles:
            # Create a simplified clean object (Raw Event)
            message = {
                'source': article['source']['name'],
                'author': article['author'],
                'title': article['title'],
                'url': article['url'],
                'publishedAt': article['publishedAt'],
                'category': category # Adding metadata
            }

            # SEND TO KAFKA
            # Here is the magic: We use 'category' as the Key.
            # Kafka will hash 'sports' and send all sports news to the same partition.
            producer.send(
                TOPIC_NAME,
                key=category,   # <--- The Logical Key
                value=message   # <--- The Data
            )
            
            print(f"Sent: {message['title'][:50]}...")
            time.sleep(0.1) # Simulate some delay

    # Force send any remaining messages
    producer.flush()
    producer.close()
    print("\nDone! All articles sent to Kafka.")

if __name__ == '__main__':
    run_producer()