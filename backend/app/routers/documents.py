import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.rag_engine import RAGEngine

router = APIRouter(prefix="/api/documents", tags=["Documents"])

rag_engine = RAGEngine()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    tenant: str = Form(...),
    title: str = Form(...),
):
    """Upload and index a document for a tenant."""

    # Validate file type
    allowed_extensions = {".pdf", ".html", ".htm", ".md", ".txt"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(allowed_extensions)}",
        )

    # Save file to disk
    tenant_dir = os.path.join(UPLOAD_DIR, tenant)
    os.makedirs(tenant_dir, exist_ok=True)
    file_path = os.path.join(tenant_dir, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Delete existing chunks for this file (if re-uploading)
    rag_engine.delete_document(tenant, file.filename)

    # Process and index
    chunk_count = rag_engine.ingest_document(file_path, title, tenant)

    return {
        "message": f"Document '{title}' indexed successfully",
        "filename": file.filename,
        "chunk_count": chunk_count,
    }


@router.get("/list")
async def list_documents(tenant: str):
    """List all indexed documents for a tenant."""
    docs = rag_engine.get_document_list(tenant)
    return {"tenant": tenant, "documents": docs}


@router.delete("/delete")
async def delete_document(tenant: str, filename: str):
    """Delete a document and its chunks from the index."""
    rag_engine.delete_document(tenant, filename)

    # Also delete the file from disk
    file_path = os.path.join(UPLOAD_DIR, tenant, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    return {"message": f"Document '{filename}' deleted successfully"}
