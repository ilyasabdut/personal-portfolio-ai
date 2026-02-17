#!/usr/bin/env python3
"""
Script to clear Qdrant collection and reindex data with custom separator
"""

import sys
sys.path.insert(0, '/home/ubuntu/repository/personal-portfolio-ai')

from src.application.rag import get_qdrant_client, COLLECTION_NAME, index_chunks
from qdrant_client.http.models import VectorParams, Distance

# Data to index
data = """Type: Summary
Category: Personal Info
Content: Ilyas Abduttawab is a Senior Fullstack Engineer based in Jakarta, Indonesia. He has over 5 years of experience developing scalable, production-ready applications. He specializes in React and Vite for frontend, and NestJS, FastAPI, and Flask for backend. He has strong DevOps skills with AWS, Docker, and CI/CD. He is currently experimenting with vector databases (Weaviate, pgvector) and LLM deployment (XInference, Ollama).
---
Type: Contact
Category: Personal Info
Content: Contact details for Ilyas Abduttawab: Phone +6281210670822, Email ilyasabduttawab@gmail.com. Personal Website: http://ilyasabdut.loseyourip.com/. Github: https://github.com/ilyasabdut/. LinkedIn: https://www.linkedin.com/in/ilyasabdut/.
---
Type: Education
Institution: Universitas Padjadjaran
Content: Ilyas Abduttawab holds a Bachelor of Informatics Engineering from Universitas Padjadjaran (2014 - 2018) with a GPA of 3.13.
---
Type: Experience
Company: Insignia
Role: Senior Fullstack Engineer
Dates: August 2024 – Present
Content: At Insignia (Jakarta), Ilyas Abduttawab works as a Senior Fullstack Engineer. He leads development of scalable APIs using Flask and FastAPI and maintains microservices. He implements Intent classification and RAG using Claude 3.5 Sonnet and integrates Jupyter Notebooks with Spark Autoscaling on Kubernetes. Tech Stack: Go, Python (Flask, FastAPI), Node.js (NestJS), ReactJS, Vite, ReactQuery, MySQL, MongoDB, DynamoDB, Redis, PostgreSQL, Elasticsearch, Docker, Kubernetes, AWS.
---
Type: Experience
Company: Stickearn
Role: Software Engineer
Dates: May 2022 – June 2024
Content: At Stickearn (Jakarta), Ilyas Abduttawab served as a Software Engineer. He specialized in backend development using Laravel and AdonisJS. Key achievements include optimizing legacy SQL code to reduce API response times from 25 to 5 seconds, implementing RBAC, and managing 5 concurrent projects. Tech Stack: PHP (Laravel), NodeJS (AdonisJS), MySQL, Redis, MongoDB.
---
Type: Experience
Company: Ejen2u
Role: Software Engineer
Dates: March 2021 – May 2022
Content: At Ejen2u (Selangor, Malaysia), Ilyas Abduttawab worked as a Software Engineer. He developed RESTful APIs using Laravel with Redis caching and built mobile applications using Flutter with MobX state management. He handled both backend and frontend integration. Tech Stack: PHP (Laravel), NodeJS (AdonisJS), Flutter, MySQL, Redis, MongoDB.
---
Type: Experience
Company: MASALALU
Role: Store Manager & IT Specialist
Dates: Dec 2017 – Nov 2020
Content: At MASALALU (Jakarta), Ilyas Abduttawab was a Store Manager & IT Specialist. He managed retail operations for two stores, developed company website using WordPress, and led ERP system planning. Tech Stack: Google Business, Mailchimp, WordPress.
---
Type: Experience
Company: ProcurA
Role: Software Engineer
Dates: Feb 2019 – Sept 2019
Content: At ProcurA (Jakarta), Ilyas Abduttawab worked as a Software Engineer developing web applications using AngularJS, integrating APIs, and implementing web designs. Tech Stack: AngularJS.
---
Type: Project
Tech: Go, HTMX, AlpineJs, VPS
Content: Project: Portfolio Website (2025). A personal portfolio website that includes a personal chatbot, deployed on a VPS. Built by Ilyas Abduttawab using Go, HTMX, and AlpineJs. URL: https://ilyasabdut.loseyourip.com/
---
Type: Project
Tech: FastAPI, OpenRouter, VPS
Content: Project: Portfolio AI (2025). A personal AI chatbot backend built by Ilyas Abduttawab using FastAPI and OpenRouter, deployed on a VPS. Repo: https://github.com/ilyasabdut/personal-portfolio-ai
---
Type: Project
Tech: NextJS, Go, Postgres, FastAPI
Content: Project: Money Tracker (2024 - WIP). A collaborative money management application. The frontend utilizes NextJS, while the backend is built with Go and PostgreSQL. It includes an AI component using FastAPI and OpenRouter. Links: https://money-tracker.ilyasabdut.loseyourip.com/login
---
Type: Project
Tech: ReactJS, NestJS, Github Pages, Render
Content: Project: Wallet Transaction App (2024). A crypto wallet application with a ReactJS frontend (hosted on GitHub Pages) and a NestJS backend (hosted on Render). Built by Ilyas Abduttawab. Repo: https://github.com/ilyasabdut/wallet-transaction-backend
---
Type: Project
Tech: ReactJS, ExpressJS, Hashlips Engine
Content: Project: NFT Generator (2022). A collaborative project to generate NFTs. Ilyas Abduttawab worked on the UI using ReactJS and WebSocket, and the backend using ExpressJS and Hashlips Engine. URL: https://hassei-ki-eta.vercel.app/"""

def clear_qdrant_collection():
    """Clear all data from Qdrant collection"""
    client = get_qdrant_client()
    try:
        # Delete the collection
        client.delete_collection(collection_name=COLLECTION_NAME)
        print(f"✅ Collection '{COLLECTION_NAME}' deleted successfully")
    except Exception as e:
        print(f"⚠️  Collection may not exist: {e}")

def create_chunks_from_data(data: str, separator: str = "---"):
    """Split data into chunks using custom separator"""
    sections = data.split(separator)
    chunks = []
    metadata = []

    for i, section in enumerate(sections):
        section = section.strip()
        if section:
            chunks.append(section)
            metadata.append({
                "source": "personal_data",
                "section": i + 1,
                "text": section
            })

    return chunks, metadata

def main():
    print("🔄 Starting reindexing process...")

    # Step 1: Clear existing data
    print("\n📦 Step 1: Clearing existing Qdrant data...")
    clear_qdrant_collection()

    # Step 2: Create chunks from data
    print("\n📝 Step 2: Creating chunks from data...")
    chunks, metadata = create_chunks_from_data(data)
    print(f"✅ Created {len(chunks)} chunks")

    # Step 3: Index chunks in Qdrant
    print("\n🔍 Step 3: Indexing chunks in Qdrant...")
    index_chunks(chunks, metadata)
    print(f"✅ Successfully indexed {len(chunks)} chunks")

    print("\n🎉 Reindexing complete!")

if __name__ == "__main__":
    main()
