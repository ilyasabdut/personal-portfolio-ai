#!/usr/bin/env/env python3
"""
Check what's in the Insignia chunk
"""

import sys
sys.path.insert(0, '/home/ubuntu/repository/personal-portfolio-ai')

from src.application.rag import get_qdrant_client, COLLECTION_NAME

def main():
    client = get_qdrant_client()

    # Get all chunks with vectors
    all_points = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=100,
        with_payload=True,
        with_vectors=True
    )[0]

    print(f"Total chunks: {len(all_points)}")

    for point in all_points:
        text = point.payload.get('text', '')
        if 'Insignia' in text:
            print("\n" + "="*80)
            print("⭐ INSIGNIA CHUNK FOUND:")
            print("="*80)
            print(f"ID: {point.id}")
            print(f"Vector: {'Present' if point.vector else 'None'}")
            if point.vector:
                print(f"Vector size: {len(point.vector)}")
                print(f"First 5 values: {point.vector[:5]}")
            print(f"\nFull text:")
            print(text)
            print(f"\nText length: {len(text)} characters")

if __name__ == "__main__":
    main()
