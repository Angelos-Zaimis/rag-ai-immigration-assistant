from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List

from app.services.documents.document_service import DocumentService

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

@router.post("/search")
async def search_documents(
    query: str,
    k: int = 5
):
    """Search for similar documents."""
    service = DocumentService()
    results = service.search_documents(query, k)
    
    return {
        "query": query,
        "results": [
            {
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata
            }
            for doc in results
        ]
    }

@router.delete("/collection")
async def delete_collection():
    """Delete the entire document collection (use with caution!)."""
    service = DocumentService()
    success = await service.delete_collection()
    
    if success:
        return {"message": "Collection deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete collection") 