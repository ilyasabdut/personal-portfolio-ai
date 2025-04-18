# src/routes/upload.py

import fitz  # PyMuPDF
from uuid import uuid4
from fastapi import APIRouter, File, UploadFile

from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.application.rag import index_chunks

router = APIRouter()

def is_valid_chunk(chunk: str) -> bool:
    stripped = chunk.strip()
    return (
        len(stripped) > 30 and
        not stripped.lower().startswith("job description") and
        not stripped.startswith("| ---") and
        not stripped.startswith("---")
    )

@router.post("/")
async def upload_doc(file: UploadFile = File(...)):
    if file.content_type not in {"application/pdf", "text/plain"}:
        return {"error": "Only PDF and TXT files allowed"}

    contents = await file.read()
    text_blocks = []

    # Extract text depending on file type
    if file.content_type == "application/pdf":
        doc = fitz.open(stream=contents, filetype="pdf")
        for i, page in enumerate(doc):
            text = page.get_text("text")
            for line in text.split("\n"):
                if is_valid_chunk(line):
                    text_blocks.append((line.strip(), {"source": file.filename, "page": i + 1}))
    elif file.content_type == "text/plain":
        text = contents.decode("utf-8")
        for i, line in enumerate(text.splitlines()):
            if is_valid_chunk(line):
                text_blocks.append((line.strip(), {"source": file.filename, "line": i + 1}))

    # Combine and chunk using RecursiveCharacterTextSplitter
    combined_text = "\n".join(chunk for chunk, _ in text_blocks)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(combined_text)

    # Map back to source metadata
    seen = set()
    indexed_chunks = []
    metadata = []

    for chunk in chunks:
        chunk = chunk.strip()
        if chunk and chunk not in seen:
            seen.add(chunk)
            # Optionally find matching original metadata block
            for original_chunk, meta in text_blocks:
                if original_chunk in chunk:
                    metadata.append({**meta, "text": chunk})
                    break
            else:
                metadata.append({"source": file.filename, "text": chunk})
            indexed_chunks.append(chunk)

    index_chunks(indexed_chunks, metadata)

    return {
        "status": "indexed",
        "file": file.filename,
        "chunks": len(indexed_chunks),
        "sample": metadata[:3],
    }
