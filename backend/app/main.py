from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@app.get("/")
def root():
    return {"message": "Logos API is running"}

@app.get("/search")
def search(q: str, limit: int = 10):
    embedding = model.encode(q).tolist()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT book, chapter, verse, text,
               1 - (embedding <=> %s::vector) AS similarity
        FROM verses
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, [embedding, embedding, limit])
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {
        "results": [
            {
                "book": r[0],
                "chapter": r[1],
                "verse": r[2],
                "text": r[3],
                "similarity": round(r[4], 4)
            }
            for r in rows
        ]
    }