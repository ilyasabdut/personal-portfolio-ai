# src/application/rag/__init__.py

from uuid import uuid4

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from src.configs.configs import config

model = SentenceTransformer("all-MiniLM-L6-v2")

COLLECTION_NAME = "documents"

def get_qdrant_client():
    return QdrantClient(url=config.qdrant_url, api_key=config.qdrant_api_key)


def get_embedding(texts: list[str]) -> list[list[float]]:
    return model.encode(texts, show_progress_bar=True)


def ensure_collection(vector_size: int):
    client = get_qdrant_client()
    collections = client.get_collections().collections
    if COLLECTION_NAME not in [c.name for c in collections]:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size, distance=Distance.COSINE
            ),
        )


def index_chunks(chunks: list[str], metadata: list[dict]):
    client = get_qdrant_client()
    embeddings = np.array(get_embedding(chunks)).astype("float32")
    ensure_collection(embeddings.shape[1])

    points = [
        PointStruct(
            id=str(uuid4()),
            vector=vec.tolist(),
            payload={**meta, "text": chunk},
        )
        for vec, meta, chunk in zip(embeddings, metadata, chunks)
    ]


    client.upsert(collection_name=COLLECTION_NAME, points=points)


def search_chunks(query: str, top_k: int = 5, min_score: float = 0.3) -> list[dict]:
    client = get_qdrant_client()
    query_vec = np.array(get_embedding([query])).astype("float32")[0]

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec.tolist(),
        limit=top_k,
    )
    for hit in results:
        print(f"[RAG] Score: {hit.score} | Source: {hit.payload.get('source')} | Text: {hit.payload.get('text')[:100]}...")

    return [
        {
            "text": hit.payload.get("text"),
            "source": hit.payload.get("source"),
            "page": hit.payload.get("page"),
            "score": hit.score,
        }
        for hit in results if hit.score >= min_score
    ]


def get_rag_context(query: str, top_k: int = 5) -> str:
    chunks = search_chunks(query, top_k)
    return "\n---\n".join([c["text"] for c in chunks])
