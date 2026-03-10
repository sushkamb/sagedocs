from fastapi import APIRouter, Depends, UploadFile, File, Form

from app.auth import verify_api_key
from app.routers.documents import process_upload

router = APIRouter(prefix="/api/v1", tags=["External API"])


@router.post("/documents/upload")
async def external_upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    tenant_id: str = Depends(verify_api_key),
):
    """Upload a document using an API key. Tenant is derived from the key."""
    return await process_upload(file, tenant_id, title)
