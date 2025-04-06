# src/routes/upload.py

import fitz  # PyMuPDF
from fastapi import APIRouter, File, UploadFile

from src.application.rag import index_chunks

router = APIRouter()


@router.post("/")
async def upload_doc(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {"error": "Only PDF files allowed"}

    contents = await file.read()
    doc = fitz.open(stream=contents, filetype="pdf")

    chunks = []
    metadata = []

    for i, page in enumerate(doc):
        text = page.get_text("text")
        for para in text.split("\n"):
            chunk = para.strip()
            if chunk:
                chunks.append(chunk)
                metadata.append(
                    {"source": file.filename, "page": i + 1, "text": chunk}
                )

    index_chunks(chunks, metadata)

    return {
        "status": "indexed",
        "file": file.filename,
        "chunks": len(chunks),
        "sample": metadata[:3],
    }
