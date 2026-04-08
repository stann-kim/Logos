from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer("multi-qa-mpnet-base-dot-v1")

db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=os.getenv("DATABASE_URL")
)

@app.get("/health")
def health():
    try:
        conn = db_pool.getconn()
        db_pool.putconn(conn)
        db_status = "ok"
    except Exception:
        db_status = "unreachable"
    
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "model": "multi-qa-mpnet-base-dot-v1",
        "database": db_status
    }

@app.get("/")
def root():
    return {"message": "Logos API is running"}

@app.get("/search")
def search(
    q: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(default=10, ge=1, le=50)
):
    try:
        embedding = model.encode(f"Bible verses about {q}").tolist()
        conn = db_pool.getconn()
        try:
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
        finally:
            db_pool.putconn(conn)

        return {
            "query": q,
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))