import json
import os
from sentence_transformers import SentenceTransformer
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
DATA_PATH = "data/niv.json"
TRANSLATION = "NIV"
BATCH_SIZE = 64

def get_connection():
    return psycopg2.connect(DB_URL)

def load_verses(path):
    with open(path, "r") as f:
        data = json.load(f)
    
    verses = []
    for book, chapters in data.items():
        for chapter, verse_map in chapters.items():
            for verse, text in verse_map.items():
                verses.append({
                    "book": book,
                    "chapter": int(chapter),
                    "verse": int(verse),
                    "text": text,
                    "translation": TRANSLATION
                })
    return verses

def seed():
    print("Loading verses...")
    verses = load_verses(DATA_PATH)
    print(f"Loaded {len(verses)} verses")

    print("Loading model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Generating embeddings...")
    texts = [v["text"] for v in verses]
    embeddings = model.encode(texts, batch_size=BATCH_SIZE, show_progress_bar=True)

    print("Inserting into database...")
    conn = get_connection()
    cur = conn.cursor()

    for i, verse in enumerate(verses):
        cur.execute("""
            INSERT INTO verses (book, chapter, verse, translation, text, embedding)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            verse["book"],
            verse["chapter"],
            verse["verse"],
            verse["translation"],
            verse["text"],
            embeddings[i].tolist()
        ))

    conn.commit()
    cur.close()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    seed()