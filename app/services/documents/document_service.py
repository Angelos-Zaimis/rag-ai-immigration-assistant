from typing import List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from qdrant_client import QdrantClient
from app.services.search.qdrant_search_service import QdrantSearchService

class DocumentService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )
        self.qdrant_search_service = QdrantSearchService()

    @staticmethod
    def ensure_metadata_completeness(metadata: dict) -> dict:
        default_keys = {
            "author": "Unknown Author",
            "year": "n.d.",
            "title": "Untitled",
            "url": ""
        }
        enriched = {key: metadata.get(key, default_keys[key]) for key in default_keys}
        return {**metadata, **enriched}

    async def add_text_document(self, text: str, metadata: dict = None) -> bool:
        try:
            document = Document(
                page_content=text,
                metadata=self.ensure_metadata_completeness(metadata or {})
            )
            text_chunks = self.text_splitter.split_documents([document])
            filtered_chunks = [chunk for chunk in text_chunks if len(chunk.page_content.strip()) > 30]
            self.qdrant_search_service.vector_store.add_documents(filtered_chunks)
            return True
        except Exception as e:
            print(f"Error adding text document: {e}")
            return False

    async def handle_upload_pdf_file(self, file_path: str, metadata: dict = None) -> bool:
        try:
            pdf_loader = PyPDFLoader(file_path)
            pdf_documents = pdf_loader.load()
            for document in pdf_documents:
                enriched_meta = self.ensure_metadata_completeness(metadata or {})
                enriched_meta['source_file'] = file_path
                document.metadata.update(enriched_meta)

            pdf_chunks = self.text_splitter.split_documents(pdf_documents)
            filtered_chunks = [chunk for chunk in pdf_chunks if len(chunk.page_content.strip()) > 30]
            self.qdrant_search_service.vector_store.add_documents(filtered_chunks)

            print(f"Ingested {len(pdf_documents)} pages, split into {len(filtered_chunks)} chunks.")
            return True
        except Exception as e:
            print(f"Error adding PDF file: {e}")
            return False

    async def add_multiple_documents(self, documents: List[Document]) -> bool:
        try:
            document_chunks = []
            for document in documents:
                document.metadata = self.ensure_metadata_completeness(document.metadata)
                chunks = self.text_splitter.split_documents([document])
                filtered_chunks = [chunk for chunk in chunks if len(chunk.page_content.strip()) > 30]
                document_chunks.extend(filtered_chunks)

            self.qdrant_search_service.vector_store.add_documents(document_chunks)
            return True
        except Exception as e:
            print(f"Error adding multiple documents: {e}")
            return False

    def search_documents(self, query: str, k: int = 5) -> List[Document]:
        return self.qdrant_search_service.search_similarity(query, k)

    def get_collection_info(self) -> dict:
        try:
            qdrant_client = QdrantClient(host="localhost", port=6333)
            collection_info = qdrant_client.get_collection(self.qdrant_search_service.collection_name)

            points, _ = qdrant_client.scroll(
                collection_name=self.qdrant_search_service.collection_name,
                limit=100,
                with_payload=True,
                with_vectors=False
            )

            decoded_points = [
                {
                    "id": point.id,
                    "payload": point.payload,
                    "vector": point.vector if point.vector else None
                } for point in points
            ]

            return {
                "collection_name": self.qdrant_search_service.collection_name,
                "points_count": collection_info.points_count,
                "status": collection_info.status,
                "sample_points": decoded_points
            }

        except Exception as e:
            return {"error": str(e)}

    async def delete_collection(self) -> bool:
        try:
            qdrant_client = QdrantClient(host="localhost", port=6333)
            qdrant_client.delete_collection(self.qdrant_search_service.collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False