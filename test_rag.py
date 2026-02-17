#!/usr/bin/env python3
"""
Test RAG system to debug why Insignia chunk isn't being retrieved
"""

import sys
sys.path.insert(0, '/home/ubuntu/repository/personal-portfolio-ai')

from src.application.rag import get_qdrant_client, COLLECTION_NAME, get_embedding
import numpy as np

def main():
    client = get_qdrant_client()

    # Get all chunks
    all_points = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=100,
        with_payload=True
    )[0]

    print(f"Total chunks in Qdrant: {len(all_points)}")
    print("\n" + "="*80)

    # Find Insignia chunk
    insig_chunks = []
    for point in all_points:
        text = point.payload.get('text', '')
        if 'Insignia' in text:
            insig_chunks.append(point)

    print(f"\n🔍 Found {len(insig_chunks)} Insignia chunk(s):")
    for i, chunk in enumerate(insig_chunks, 1):
        print(f"\n--- Insignia Chunk {i} ---")
        print(chunk.payload.get('text', '')[:200] + "...")

    # Test search for "which company now?"
    print("\n" + "="*80)
    print("\n🔍 Testing search for: 'which company now?'")
    print("="*80)

    query = "which company now?"
    query_vec = np.array(get_embedding([query])).astype("float32")[0]

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec.tolist(),
        limit=10,
    )

    print(f"\n📊 Search results (top {len(results)}):")
    for i, hit in enumerate(results, 1):
        text = hit.payload.get('text', '')
        print(f"\n--- Result {i} (Score: {hit.score:.4f}) ---")
        print(f"First 150 chars: {text[:150]}...")
        if 'Insignia' in text:
            print("⭐ THIS IS THE INSIGNIA CHUNK!")

    # Check if Insignia is in results
    insig_in_results = any('Insignia' in hit.payload.get('text', '') for hit in results)
    print(f"\n{'✅' if insig_in_results else '❌'} Insignia chunk in search results: {insig_in_results}")

if __name__ == "__main__":
    main()
