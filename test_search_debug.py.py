#!/usr/bin/env/env python3
"""
Debug RAG search to see all scores
"""

import sys
sys.path.insert(0, '/home/ubuntu/repository/personal-portfolio-ai')

from src.application.rag import get_qdrant_client, COLLECTION_NAME, get_embedding
import numpy as np

def main():
    client = get_qdrant_client()

    query = "where does ilyas work in 2025?"
    print(f"🔍 Testing search for: '{query}'")
    print("="*80)

    query_vec = np.array(get_embedding([query])).astype("float32")[0]

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec.tolist(),
        limit=10,
    )

    print(f"\n📊 All search results (before filtering):")
    for i, hit in enumerate(results, 1):
        text = hit.payload.get('text', '')
        print(f"\n--- Result {i} (Score: {hit.score:.4f}) ---")
        print(f"Text preview: {text[:100]}...")
        if 'Insignia' in text:
            print("⭐ THIS IS THE INSIGNIA CHUNK!")

if __name__ == "__main__":
    main()
