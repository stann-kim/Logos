from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from psycopg2 import pool
import os
from dotenv import load_dotenv
import time
import logging
import httpx

load_dotenv()

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

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
    limit: int = Query(default=5, ge=1, le=50)
):
    start = time.time()
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

        latency = round((time.time() - start) * 1000)
        logger.info(f"query='{q}' results={len(rows)} latency={latency}ms")

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
        logger.error(f"query='{q}' error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/context/{book}/{chapter}/{verse}")
async def get_context(book: str, chapter: int, verse: int):
    start = time.time()
    try:
        conn = db_pool.getconn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT text FROM verses
                WHERE book = %s AND chapter = %s AND verse = %s
                LIMIT 1
            """, [book, chapter, verse])
            row = cur.fetchone()
            cur.close()
        finally:
            db_pool.putconn(conn)

        if not row:
            raise HTTPException(status_code=404, detail="Verse not found")

        verse_text = row[0]

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "http://host.docker.internal:11434/api/generate",
                json={
                    "model": "qwen3",
                    "prompt": f"""Give historical and literary context for this Bible verse in 3 sections.
Be concise — 5 sentences per section max.

Verse: {book} {chapter}:{verse} — "{verse_text}"

Format your response exactly like this:
BOOK INTRO: [who wrote this book, when, what was going on during the time it was written, and to whom if it was written to someone]
PASSAGE CONTEXT: [what is happening in the current chapter with details and provide context from other chapters/verses if needed]
CULTURAL NOTES: [any cultural, linguistic, historic, or cross-reference insights]""",
                    "stream": False
                }
            )

        raw = response.json()["response"].strip()
        sections = {}
        for line in raw.split("\n"):
            if line.startswith("BOOK INTRO:"):
                sections["book_intro"] = line.replace("BOOK INTRO:", "").strip()
            elif line.startswith("PASSAGE CONTEXT:"):
                sections["passage_context"] = line.replace("PASSAGE CONTEXT:", "").strip()
            elif line.startswith("CULTURAL NOTES:"):
                sections["cultural_notes"] = line.replace("CULTURAL NOTES:", "").strip()

        latency = round((time.time() - start) * 1000)
        logger.info(f"context={book} {chapter}:{verse} latency={latency}ms")

        return {
            "book": book,
            "chapter": chapter,
            "verse": verse,
            "text": verse_text,
            "context": sections
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"context error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/verse")
def get_verse(ref: str = Query(...)):
    try:
        # Parse "John 3:16" → book="John", chapter=3, verse=16
        import re
        match = re.match(r"^(.+?)\s+(\d+):(\d+)$", ref.strip())
        if not match:
            raise HTTPException(status_code=400, detail="Invalid format. Use e.g. 'John 3:16'")
        
        book = match.group(1).strip()
        chapter = int(match.group(2))
        verse = int(match.group(3))

        conn = db_pool.getconn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT book, chapter, verse, text
                FROM verses
                WHERE LOWER(book) = LOWER(%s) AND chapter = %s AND verse = %s
                LIMIT 1
            """, [book, chapter, verse])
            row = cur.fetchone()
            cur.close()
        finally:
            db_pool.putconn(conn)

        if not row:
            raise HTTPException(status_code=404, detail="Verse not found")

        return {
            "results": [{
                "book": row[0],
                "chapter": row[1],
                "verse": row[2],
                "text": row[3],
                "similarity": 1.0
            }]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"verse lookup error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))