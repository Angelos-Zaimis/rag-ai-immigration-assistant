#!/usr/bin/env python3
"""
Script to add documents to Qdrant vector database.
Run this script to populate your local Qdrant with sample documents.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Load environment variables
load_dotenv()

def add_sample_documents():
    """Add sample immigration-related documents to Qdrant."""
    
    print("🚀 Starting to add documents to Qdrant...")
    
    # Initialize Qdrant client and embeddings
    client = QdrantClient(host="localhost", port=6333)
    embeddings = OpenAIEmbeddings()
    
    # Sample immigration documents (you can replace with your real docs)
    sample_docs = [
        {
            "content": """
            Swiss residence permits are categorized into several types:
            - B permit (Residence permit): For foreign nationals who intend to stay in Switzerland for more than one year
            - C permit (Settlement permit): For long-term residents after 5-10 years
            - L permit (Short-term residence permit): For stays up to one year
            - G permit (Cross-border commuter permit): For workers living abroad but working in Switzerland
            """,
            "metadata": {"source": "swiss_permits.pdf", "topic": "residence_permits"}
        },
        {
            "content": """
            Work permit requirements in Switzerland:
            1. EU/EFTA citizens have free movement and can work without additional permits
            2. Non-EU citizens need a work permit before starting employment
            3. Employers must prove no suitable EU/Swiss candidate is available
            4. Skilled workers have better chances for permits
            5. Annual quotas limit non-EU work permits
            """,
            "metadata": {"source": "work_permits.pdf", "topic": "work_permits"}
        },
        {
            "content": """
            Swiss citizenship requirements:
            - 10 years of residence in Switzerland (periods between ages 8-18 count double)
            - C permit holder
            - Integration requirements: language skills (B2 level), knowledge of Switzerland
            - No criminal record
            - Respect for Swiss legal order
            - No threat to internal or external security
            """,
            "metadata": {"source": "citizenship.pdf", "topic": "citizenship"}
        },
        {
            "content": """
            Family reunification in Switzerland:
            Spouses and unmarried children under 21 can join:
            - Swiss citizens immediately
            - C permit holders immediately  
            - B permit holders after integration requirements are met
            Required documents: marriage certificate, birth certificates, proof of accommodation, financial means
            """,
            "metadata": {"source": "family_reunification.pdf", "topic": "family"}
        },
        {
            "content": """
            Student visa for Switzerland:
            - Acceptance letter from Swiss educational institution
            - Proof of financial means (CHF 18,000-24,000 per year)
            - Health insurance
            - Clean criminal record
            - L permit for studies under 1 year, B permit for longer studies
            - Can work part-time (15 hours/week during studies)
            """,
            "metadata": {"source": "student_visa.pdf", "topic": "student_visa"}
        }
    ]
    
    # Convert to LangChain documents
    documents = []
    for doc in sample_docs:
        documents.append(Document(
            page_content=doc["content"].strip(),
            metadata=doc["metadata"]
        ))
    
    # Split documents into chunks (optional, for larger documents)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )
    
    split_docs = text_splitter.split_documents(documents)
    print(f"📄 Split {len(documents)} documents into {len(split_docs)} chunks")
    
    # Create collection and add documents
    try:
        collection_name = "immigration_docs"
        
        # Create Qdrant vector store and add documents
        vector_store = Qdrant.from_documents(
            split_docs,
            embeddings,
            url="http://localhost:6333",
            collection_name=collection_name,
        )
        
        print(f"✅ Successfully added {len(split_docs)} document chunks to collection '{collection_name}'")
        
        # Test the search
        print("\n🔍 Testing search functionality...")
        results = vector_store.similarity_search("How to get work permit in Switzerland?", k=2)
        
        print(f"Found {len(results)} relevant documents:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.metadata}")
            print(f"   Content: {result.page_content[:100]}...")
            
    except Exception as e:
        print(f"❌ Error adding documents: {e}")
        return False
    
    return True

def check_collection_status():
    """Check the current status of collections in Qdrant."""
    client = QdrantClient(host="localhost", port=6333)
    
    try:
        collections = client.get_collections()
        print(f"\n📊 Collections in Qdrant: {len(collections.collections)}")
        
        for collection in collections.collections:
            info = client.get_collection(collection.name)
            print(f"  - {collection.name}: {info.points_count} documents")
            
    except Exception as e:
        print(f"❌ Error checking collections: {e}")

if __name__ == "__main__":
    print("🔧 Qdrant Document Loader")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found. Please set it in your .env file.")
        sys.exit(1)
    
    # Check current status
    check_collection_status()
    
    # Add documents
    success = add_sample_documents()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ Documents successfully added to Qdrant!")
        check_collection_status()
    else:
        print("\n❌ Failed to add documents.") 