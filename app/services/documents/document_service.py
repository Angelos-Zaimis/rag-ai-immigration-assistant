"""
Document service for uploading and processing documents to Qdrant vector database.
"""

import os
from typing import List, Optional
from io import BytesIO

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

from app.services.search.qdrant_search_service import QdrantSearchService


class DocumentService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.qdrant_service = QdrantSearchService()

    async def add_text_document(self, text: str, metadata: dict = None) -> bool:
        """Add a text document to the vector database."""
        try:
            # Create document
            doc = Document(
                page_content=text,
                metadata=metadata or {}
            )
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Add to vector store
            for chunk in chunks:
                self.qdrant_service.vector_store.add_documents([chunk])
            
            return True
        except Exception as e:
            print(f"Error adding text document: {e}")
            return False

    async def add_pdf_file(self, file_path: str, metadata: dict = None) -> bool:
        """Add a PDF file to the vector database."""
        try:
            # Load PDF
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Add metadata to each document
            for doc in documents:
                doc.metadata.update(metadata or {})
                doc.metadata['source_file'] = file_path
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Add to vector store
            self.qdrant_service.vector_store.add_documents(chunks)
            
            return True
        except Exception as e:
            print(f"Error adding PDF file: {e}")
            return False

    async def add_multiple_documents(self, documents: List[Document]) -> bool:
        """Add multiple documents to the vector database."""
        try:
            # Split all documents into chunks
            all_chunks = []
            for doc in documents:
                chunks = self.text_splitter.split_documents([doc])
                all_chunks.extend(chunks)
            
            # Add all chunks to vector store
            self.qdrant_service.vector_store.add_documents(all_chunks)
            
            return True
        except Exception as e:
            print(f"Error adding multiple documents: {e}")
            return False

    def search_documents(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents."""
        return self.qdrant_service.search_similarity(query, k)

    def get_collection_info(self) -> dict:
        """Get information about the current collection."""
        try:
            client = QdrantClient(host="localhost", port=6333)
            collection_info = client.get_collection(self.qdrant_service.collection_name)
            
            return {
                "collection_name": self.qdrant_service.collection_name,
                "points_count": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            return {"error": str(e)}

    async def delete_collection(self) -> bool:
        """Delete the entire collection (use with caution!)."""
        try:
            client = QdrantClient(host="localhost", port=6333)
            client.delete_collection(self.qdrant_service.collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False 