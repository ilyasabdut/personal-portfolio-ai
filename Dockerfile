# syntax=docker/dockerfile:1.4

# --- Base image ---
FROM python:3.12-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies for pymupdf and sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install pip tools
RUN pip install --upgrade pip

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY src ./src
COPY run.py ./run.py

# Install Python deps from pyproject.toml
RUN pip install --no-cache-dir .


# Optional: preload the sentence-transformers model to speed up container startup
RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Expose FastAPI port
EXPOSE 8000

# Healthcheck using FastAPI endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Start FastAPI using Uvicorn
CMD ["python" , "run.py"]
    