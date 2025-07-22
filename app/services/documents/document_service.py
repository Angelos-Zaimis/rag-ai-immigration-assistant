"""
Document service for uploading and processing documents to Qdrant vector database.
"""

from typing import List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from qdrant_client import QdrantClient

from app.services.search.qdrant_search_service import QdrantSearchService


class DocumentService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.qdrant_search_service = QdrantSearchService()

    async def add_text_document(self, text: str, metadata: dict = None) -> bool:
        """Add a text document to the vector database."""
        try:
            # Create document
            document = Document(
                page_content=text,
                metadata=metadata or {}
            )
            
            # Split into chunks
            text_chunks = self.text_splitter.split_documents([document])
            
            # Add to vector store
            for chunk in text_chunks:
                self.qdrant_search_service.vector_store.add_documents([chunk])
            
            return True
        except Exception as e:
            print(f"Error adding text document: {e}")
            return False

    async def add_pdf_file(self, file_path: str, metadata: dict = None) -> bool:
        """Add a PDF file to the vector database."""
        try:
            # Load PDF
            pdf_loader = PyPDFLoader(file_path)
            pdf_documents = pdf_loader.load()
            
            # Add metadata to each document
            for document in pdf_documents:
                document.metadata.update(metadata or {})
                document.metadata['source_file'] = file_path
            
            # Split into chunks
            pdf_chunks = self.text_splitter.split_documents(pdf_documents)
            
            # Add to vector store
            self.qdrant_search_service.vector_store.add_documents(pdf_chunks)
            
            return True
        except Exception as e:
            print(f"Error adding PDF file: {e}")
            return False

    async def add_multiple_documents(self, documents: List[Document]) -> bool:
        """Add multiple documents to the vector database."""
        try:
            # Split all documents into chunks
            document_chunks = []
            for document in documents:
                chunks = self.text_splitter.split_documents([document])
                document_chunks.extend(chunks)
            
            # Add all chunks to vector store
            self.qdrant_search_service.vector_store.add_documents(document_chunks)
            
            return True
        except Exception as e:
            print(f"Error adding multiple documents: {e}")
            return False

    def search_documents(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents."""
        return self.qdrant_search_service.search_similarity(query, k)

    def get_collection_info(self) -> dict:
        """Get information about the current collection."""
        try:
            qdrant_client = QdrantClient(host="localhost", port=6333)
            collection_info = qdrant_client.get_collection(self.qdrant_search_service.collection_name)
            
            return {
                "collection_name": self.qdrant_search_service.collection_name,
                "points_count": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            return {"error": str(e)}

    async def delete_collection(self) -> bool:
        """Delete the entire collection (use with caution!)."""
        try:
            qdrant_client = QdrantClient(host="localhost", port=6333)
            qdrant_client.delete_collection(self.qdrant_search_service.collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False 