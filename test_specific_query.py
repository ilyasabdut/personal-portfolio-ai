#!/usr/bin/env/env python3
"""
Test specific query: where does ilyas work in 2025?
"""

import sys
sys.path.insert(0, '/home/ubuntu/repository/personal-portfolio-ai')

from src.application.rag import get_qdrant_client, COLLECTION_NAME, get_embedding, search_chunks
import numpy as np

def main():
    client = get_qdrant_client()

    query = "where does ilyas work in 2025?"
    print(f"🔍 Testing search for: '{query}'")
    print("="*80)

    # Test with different thresholds
    for threshold in [0.1, 0.15, 0.2, 0.25, 0.3]:
        print(f"\n--- Testing with min_score={threshold} ---")
        results = search_chunks(query, top_k=10, min_score=threshold)

        insig_found = any('Insignia' in r['text'] for r in results)
        print(f"Threshold {threshold}: {'✅ Found' if insig_found else '❌ Not found'} ({len(results)} chunks)")

        if insig_found:
            for r in results:
                if 'Insignia' in r['text']:
                    print(f"  Insignia score: {r['score']:.4f}")
                    print(f"  Text: {r['text'][:150]}...")

if __name__ == "__main__":
    main()
