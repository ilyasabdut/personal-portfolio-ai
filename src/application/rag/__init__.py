# src/application/rag/__init__.py

import sqlite3
from pathlib import Path
from uuid import uuid4

import numpy as np
from sentence_transformers import SentenceTransformer
from sqlite_vec import load

from src.configs.configs import config

model = SentenceTransformer("all-MiniLM-L6-v2")
DEFAULT_VECTOR_DIM = 384


def get_sqlite_vec_client(db_path: str | None = None):
    """Get or create a sqlite-vec database connection"""
    from src.configs.configs import config

    if db_path is None:
        db_path = config.sqlite_db_path

    db_path = Path(db_path).as_posix()
    conn = sqlite3.connect(db_path)
    load(conn)

    cursor = conn.cursor()
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS documents USING vec0(
            embedding float[384],
            text TEXT,
            source TEXT,
            page INTEGER
        )
    """)
    conn.commit()

    return conn


def get_embedding(texts: list[str]) -> list[list[float]]:
    return model.encode(texts, show_progress_bar=True)


def ensure_collection(vector_size: int = 384):
    client = get_sqlite_vec_client()
    cursor = client.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='documents'"
    )
    if not cursor.fetchone():
        raise ValueError("Documents table not found")


def index_chunks(chunks: list[str], metadata: list[dict]):
    client = get_sqlite_vec_client()
    embeddings = np.array(get_embedding(chunks)).astype("float32")
    ensure_collection(embeddings.shape[1])

    cursor = client.cursor()

    for vec, meta, chunk in zip(embeddings, metadata, chunks):
        vec_blob = vec.tobytes()
        cursor.execute(
            """
            INSERT INTO documents (rowid, embedding, text, source, page)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                hash(str(uuid4())) % (2**31),
                vec_blob,
                chunk,
                meta.get("source"),
                meta.get("page"),
            ),
        )

    client.commit()


def search_chunks(
    query: str, top_k: int = 10, min_score: float = 0.0
) -> list[dict]:
    print(f"[RAG] Searching for: {query}")
    client = get_sqlite_vec_client()
    query_vec = np.array(get_embedding([query])).astype("float32")[0]

    cursor = client.cursor()
    cursor.execute(
        """
        SELECT rowid, text, source, page, distance
        FROM documents
        WHERE embedding MATCH ?
        ORDER BY distance
        LIMIT ?
        """,
        (query_vec.tobytes(), top_k),
    )

    results = cursor.fetchall()
    print(f"[RAG] Found {len(results)} results")

    formatted_results = []
    for row in results:
        rowid, text, source, page, distance = row
        similarity = 1.0 / (1.0 + distance) if distance > 0 else 1.0

        if similarity >= min_score:
            print(
                f"[RAG] Score: {similarity:.4f} | Source: {source} | Text: {text[:100] if text else 'N/A'}..."
            )
            formatted_results.append(
                {
                    "text": text,
                    "source": source,
                    "page": page,
                    "score": similarity,
                }
            )

    return formatted_results


def get_rag_context(query: str, top_k: int = 10) -> str:
    chunks = search_chunks(query, top_k)
    print(f"Retrieved chunks: {chunks}")

    from datetime import datetime

    current_year = datetime.now().year
    keywords = [
        "currently",
        "current",
        "now",
        "today",
        "present",
        "sekarang",
        "skrg",
        "kini",
        "sekar",
        "saat ini",
    ]
    year_keywords = [str(y) for y in range(current_year - 2, current_year + 1)]

    if any(keyword in query.lower() for keyword in keywords + year_keywords):
        has_insignia = any("Insignia" in c.get("text", "") for c in chunks)
        if not has_insignia:
            insignia_results = search_chunks(
                "Insignia Senior Fullstack Engineer", top_k=3
            )
            for r in insignia_results:
                if "Insignia" in r.get("text", ""):
                    chunks.insert(0, r)
                    print(
                        f"[RAG] Added Insignia result for current work query"
                    )
                    break

    return "\n---\n".join([c["text"] for c in chunks])
