import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List

from app.services.documents.document_service import DocumentService
from controllers.document_controller import DocumentController

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload-text")
async def upload_text_document(
    text: str,
    source: str = "api_upload",
    topic: str = "general"
):
    """Upload a text document to the vector database."""
    service = DocumentService()
    
    metadata = {
        "source": source,
        "topic": topic,
        "upload_method": "api"
    }
    
    success = await service.add_text_document(text, metadata)
    
    if success:
        return {"message": "Document uploaded successfully", "metadata": metadata}
    else:
        raise HTTPException(status_code=500, detail="Failed to upload document")

@router.get("/collection-info")
async def get_collection_info():
    """Get information about the document collection."""
    service = DocumentService()
    info = service.get_collection_info()
    return info

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    temp_filename = f"/tmp/{uuid4()}_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    controller = DocumentController()
    result = await controller.upload_pdf(temp_filename)

    os.remove(temp_filename)

    return result
