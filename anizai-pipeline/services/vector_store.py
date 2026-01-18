import chromadb
import os

class VectorStore:
    def __init__(self, db_path="data/chroma_db", collection_name="news_articles"):
        """
        מאתחל את החיבור למסד הנתונים הוקטורי (ChromaDB).
        המידע יישמר בתיקייה מקומית כדי שלא ילך לאיבוד.
        """
        # חישוב הנתיב האבסולוטי כדי למנוע בעיות
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.persist_directory = os.path.join(base_dir, db_path)
        
        # יצירת הקליינט (Persistent אומר שזה נשמר בדיסק)
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # יצירה או שליפה של האוסף (כמו טבלה)
        # אנחנו משתמשים ב-get_or_create כדי לא לדרוס מידע קיים
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
        print(f"🔹 Connected to Vector DB at: {self.persist_directory}")
        print(f"🔹 Collection '{collection_name}' loaded. Current count: {self.collection.count()}")

    def add_article(self, article_id, text, embedding, metadata):
        """
        מוסיף כתבה אחת למסד הנתונים.
        """
        try:
            self.collection.add(
                ids=[article_id],          # המזהה הייחודי
                documents=[text],          # הטקסט המקורי (לצורך שליפה ב-RAG)
                embeddings=[embedding],    # הוקטור (לצורך חיפוש)
                metadatas=[metadata]       # מידע נוסף (כותרת, תאריך, מקור)
            )
            return True
        except Exception as e:
            print(f"❌ Error adding to DB: {e}")
            return False

    def search(self, query_embedding, n_results=3):
        """
        מבצע חיפוש סמנטי: מקבל וקטור של שאלה, ומחזיר את הכתבות הכי דומות.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results

# --- בדיקה קטנה (לא תרוץ כשיובא מבחוץ) ---
if __name__ == "__main__":
    # זה ייצור את תיקיית data/chroma_db בפעם הראשונה
    store = VectorStore()