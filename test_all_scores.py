#!/usr/bin/env/env python3
"""
Test search for all chunks to see Insignia's actual score
"""

import sys
sys.path.insert(0, '/home/ubuntu/repository/personal-portfolio-ai')

from src.application.rag import get_qdrant_client, COLLECTION_NAME, get_embedding
import numpy as np

def main():
    query = "where does ilyas work in 2025?"
    print(f"🔍 Searching for: '{query}'")
    print("="*80)

    client = get_qdrant_client()
    query_vec = np.array(get_embedding([query])).astype("float32")[0]

    # Search for ALL chunks (not just top 10)
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec.tolist(),
        limit=100,  # Get all chunks
    )

    print(f"\n📊 All {len(results)} chunks with scores:")
    print("="*80)

    for i, hit in enumerate(results, 1):
        text = hit.payload.get('text', '')
        company = ''
        if 'Company:' in text:
            for line in text.split('\n'):
                if line.startswith('Company:'):
                    company = line.replace('Company:', '').strip()
                    break

        marker = '⭐' if 'Insignia' in text else '  '
        print(f"{marker} {i:2d}. Score: {hit.score:.4f} | {company:20s} | {text[:60]}...")

if __name__ == "__main__":
    main()
