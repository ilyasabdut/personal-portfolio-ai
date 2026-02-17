#!/usr/bin/env python3
"""
Script to verify Qdrant index
"""

import sys
sys.path.insert(0, '/home/ubuntu/repository/personal-portfolio-ai')

from src.application.rag import get_qdrant_client, COLLECTION_NAME

def main():
    client = get_qdrant_client()

    # Check if collection exists
    collections = client.get_collections().collections
    if COLLECTION_NAME in [c.name for c in collections]:
        print(f"✅ Collection '{COLLECTION_NAME}' exists")

        # Get collection info
        collection_info = client.get_collection(COLLECTION_NAME)
        print(f"📊 Points count: {collection_info.points_count}")
        print(f"📏 Vector size: {collection_info.config.params.vectors.size}")

        # Get some sample points
        points = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=3,
            with_payload=True
        )[0]

        print(f"\n📝 Sample chunks ({len(points)}):")
        for i, point in enumerate(points, 1):
            print(f"\n--- Chunk {i} ---")
            print(f"Source: {point.payload.get('source')}")
            print(f"Section: {point.payload.get('section')}")
            print(f"Text preview: {point.payload.get('text')[:100]}...")
    else:
        print(f"❌ Collection '{COLLECTION_NAME}' not found")

if __name__ == "__main__":
    main()
