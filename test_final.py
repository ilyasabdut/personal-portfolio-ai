#!/usr/bin/env/env python3
"""
Final test to verify Insignia is found
"""

import sys
sys.path.insert(0, '/home/ubuntu/repository/personal-portfolio-ai')

from src.application.rag import search_chunks

def main():
    query = "where does ilyas work in 2025?"
    print(f"🔍 Testing search for: '{query}'")
    print("="*80)

    # Test with top_k=15 to get more results
    results = search_chunks(query, top_k=15)

    print(f"\n📊 Retrieved {len(results)} chunks:")

    for i, result in enumerate(results, 1):
        text = result['text']
        marker = '⭐' if 'Insignia' in text else '  '
        print(f"{marker} {i:2d}. Score: {result['score']:.4f} | {text[:60]}...")

    insig_found = any('Insignia' in r['text'] for r in results)
    print(f"\n{'✅' if insig_found else '❌'} Insignia found: {insig_found}")

if __name__ == "__main__":
    main()
