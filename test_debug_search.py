#!/usr/bin/env/env python3
"""
Debugged search_chunks function
"""

import sys
sys.path.insert(0, '/home/ubuntu/repository/personal-portfolio-ai')

from src.application.rag import search_chunks

def main():
    query = "where does ilyas work in 2025?"
    print(f"🔍 Testing search_chunks for: '{query}'")
    print("="*80)

    # Test with different parameters
    for top_k in [5, 10, 15]:
        for min_score in [0.0, 0.1, 0.2]:
            print(f"\n--- top_k={top_k}, min_score={min_score} ---")
            results = search_chunks(query, top_k=top_k, min_score=min_score)

            print(f"Results returned: {len(results)}")

            insig_found = any('Insignia' in r['text'] for r in results)
            print(f"{'✅' if insig_found else '❌'} Insignia found: {insig_found}")

            if insig_found:
                for r in results:
                    if 'Insignia' in r['text']:
                        print(f"  Insignia score: {r['score']:.4f}")

if __name__ == "__main__":
    main()
