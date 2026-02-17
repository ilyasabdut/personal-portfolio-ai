#!/usr/bin/env/env python3
"""
Test different queries to find Insignia chunk
"""

import sys
sys.path.insert(0, '/home/ubuntu/repository/personal-portfolio-ai')

from src.application.rag import get_qdrant_client, COLLECTION_NAME, get_embedding
import numpy as np

def test_query(client, query):
    print(f"\n🔍 Testing search for: '{query}'")
    print("="*80)

    query_vec = np.array(get_embedding([query])).astype("float32")[0]

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec.tolist(),
        limit=10,
    )

    insig_found = False
    for i, hit in enumerate(results, 1):
        text = hit.payload.get('text', '')
        if 'Insignia' in text:
            print(f"⭐ Insignia found at position {i} with score: {hit.score:.4f}")
            print(f"Text: {text[:200]}...")
            insig_found = True

    if not insig_found:
        print("❌ Insignia not found in top 10 results")

    return insig_found

def main():
    client = get_qdrant_client()

    # Test different queries
    queries = [
        "current company",
        "where does ilyas work now",
        "present job",
        "latest employment",
        "current employer",
        "workplace 2024",
        "senior fullstack engineer",
        "insignia"
    ]

    for query in queries:
        test_query(client, query)

if __name__ == "__main__":
    main()
