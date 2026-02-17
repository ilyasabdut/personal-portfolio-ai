#!/usr/bin/env/env python3
"""
Direct test of Qdrant search
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

    # Test different limit values
    for limit in [5, 10, 15]:
        print(f"\n--- Testing with limit={limit} ---")
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vec.tolist(),
            limit=limit,
        )

        print(f"Total results returned: {len(results)}")

        insig_found = False
        for i, hit in enumerate(results, 1):
            text = hit.payload.get('text', '')
            if 'Insignia' in text:
                print(f"⭐ Insignia found at position {i} with score: {hit.score:.4f}")
                insig_found = True

        if not insig_found:
            print("❌ Insignia not found")

if __name__ == "__main__":
    main()
