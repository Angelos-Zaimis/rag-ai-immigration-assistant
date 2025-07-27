from langchain_openai.embeddings import OpenAIEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore

class QdrantSearchService:
    # Initializes the Qdrant client, OpenAI embeddings, and vector store
    def __init__(self, collection_name: str = "immigration_docs"):
        self.collection_name = collection_name
        self.client = QdrantClient(host="localhost", port=6333)
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )

    # Searches for the top-k most similar document chunks based on the input query
    def search_similarity(self, query: str, k: int = 5):
        try:
            results = self.vector_store.similarity_search(query=query, k=k)
            if not results:
                return []
            return [doc.page_content for doc in results]
        except Exception as e:
            print(f"Similarity search failed: {e}")
            return []
