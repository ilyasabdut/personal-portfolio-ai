# src/routes/upload.py

import fitz  # PyMuPDF
from fastapi import APIRouter, File, UploadFile

from src.application.rag import index_chunks

router = APIRouter()


@router.post("/")
async def upload_doc(file: UploadFile = File(...)):
    if file.content_type not in {"application/pdf", "text/plain"}:
        return {"error": "Only PDF and TXT files allowed"}

    contents = await file.read()

    chunks = []
    metadata = []

    if file.content_type == "application/pdf":
        doc = fitz.open(stream=contents, filetype="pdf")
        for i, page in enumerate(doc):
            text = page.get_text("text")
            for para in text.split("\n"):
                chunk = para.strip()
                if chunk:
                    chunks.append(chunk)
                    metadata.append(
                        {"source": file.filename, "page": i + 1, "text": chunk}
                    )
    elif file.content_type == "text/plain":
        text = contents.decode("utf-8")
        for i, line in enumerate(text.splitlines()):
            chunk = line.strip()
            if chunk:
                chunks.append(chunk)
                metadata.append(
                    {"source": file.filename, "line": i + 1, "text": chunk}
                )

    index_chunks(chunks, metadata)

    return {
        "status": "indexed",
        "file": file.filename,
        "chunks": len(chunks),
        "sample": metadata[:3],
    }
