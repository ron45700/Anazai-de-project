anizai-pipeline/
│
├── infrastructure/           <-- (מודול התשתית)
│   └── docker-compose.yaml   # קובץ הדוקר שהכנו (קפקא)
│
├── ingestion/                <-- (מודול 1: הבאת נתונים)
│   ├── __init__.py
│   └── news_producer.py      # היה producer.py (שנה לשם משמעותי יותר)
│
├── processing/               <-- (מודול 2: עיבוד ראשוני/Spark)
│   ├── __init__.py
│   └── silver_consumer.py    # הקוד האחרון שכתבנו (consumer_silver.py)
│
├── data/                     <-- (סימולציה ל-Data Lake/Storage)
│   ├── raw/                  # לכאן נשמור בעתיד נתונים גולמיים אם נרצה
│   └── processed/            # לכאן יישמר הקובץ processed_news.json
│
├── requirements.txt          # רשימת כל הספריות (kafka-python, requests)
└── README.md                 # הסברים לחברים איך להריץ