#!/usr/bin/env python3
"""
Script to clear sqlite-vec database and reindex data from experience.txt
"""

import sys

sys.path.insert(0, "/home/ubuntu/repository/personal-portfolio-ai")

import sqlite3
from pathlib import Path
from src.application.rag import get_sqlite_vec_client, index_chunks, config

DATA_FILE = "/home/ubuntu/repository/experience.txt"


def clear_sqlite_db():
    """Clear all data from sqlite-vec database"""
    db_path = Path(config.sqlite_db_path)
    if db_path.exists():
        db_path.unlink()
        print(f"Cleared database: {db_path}")
    else:
        print(f"Database does not exist yet: {db_path}")


def create_chunks_from_file(file_path: str, separator: str = "---"):
    """Split data into chunks using custom separator"""
    with open(file_path, "r") as f:
        data = f.read()

    sections = data.split(separator)
    chunks = []
    metadata = []

    for i, section in enumerate(sections):
        section = section.strip()
        if section:
            chunks.append(section)
            metadata.append(
                {
                    "source": "experience.txt",
                    "page": i + 1,
                }
            )

    return chunks, metadata


def main():
    print("Starting reindexing process...")

    print("\nStep 1: Clearing existing sqlite-vec data...")
    clear_sqlite_db()

    print("\nStep 2: Creating chunks from experience.txt...")
    chunks, metadata = create_chunks_from_file(DATA_FILE)
    print(f"Created {len(chunks)} chunks")

    print("\nStep 3: Indexing chunks in sqlite-vec...")
    index_chunks(chunks, metadata)
    print(f"Successfully indexed {len(chunks)} chunks")

    print("\nReindexing complete!")


if __name__ == "__main__":
    main()
