#!/usr/bin/env python3
"""
Simple test to verify RAG search works with new threshold
"""

import sys
sys.path.insert(0, '/home/ubuntu/repository/personal-portfolio-ai')

from src.application.rag import search_chunks

def main():
    query = "which company now?"
    print(f"🔍 Testing search for: '{query}'")
    print("="*80)

    results = search_chunks(query, top_k=10)

    print(f"\n📊 Retrieved {len(results)} chunks (after filtering):")
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} (Score: {result['score']:.4f}) ---")
        print(f"Text preview: {result['text'][:150]}...")
        if 'Insignia' in result['text']:
            print("⭐ THIS IS THE INSIGNIA CHUNK!")

    insig_in_results = any('Insignia' in r['text'] for r in results)
    print(f"\n{'✅' if insig_in_results else '❌'} Insignia chunk in filtered results: {insig_in_results}")

if __name__ == "__main__":
    main()
