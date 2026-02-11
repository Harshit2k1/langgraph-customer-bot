import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.processing.document_processor import DocumentProcessor
from src.database.vector_db import VectorStore
from src.config import Config

def ingest_sample_policies():
    """Ingest sample policy documents into vector store"""
    
    policy_dir = "./data/sample_policies/"
    
    if not os.path.exists(policy_dir):
        print(f"Policy directory not found: {policy_dir}")
        print("Run generate_policies.py first")
        return False
    
    try:
        print("Initializing document processor...")
        processor = DocumentProcessor()
        
        print("Initializing vector store...")
        vector_store = VectorStore()
        
        print(f"\nProcessing PDFs from {policy_dir}")
        all_chunks = processor.process_directory(policy_dir)
        
        if not all_chunks:
            print("No chunks generated from PDFs")
            return False
        
        print(f"\nPreparing {len(all_chunks)} chunks for ingestion...")
        
        documents = [chunk['text'] for chunk in all_chunks]
        metadatas = [chunk['metadata'] for chunk in all_chunks]
        ids = [f"chunk_{i}" for i in range(len(all_chunks))]
        
        print("Ingesting documents into ChromaDB...")
        success = vector_store.add_documents(documents, metadatas, ids)
        
        if success:
            stats = vector_store.get_collection_stats()
            print(f"\nIngestion complete!")
            print(f"Total documents in collection: {stats['total_documents']}")
            return True
        else:
            print("Ingestion failed")
            return False
            
    except Exception as e:
        print(f"Error during ingestion: {e}")
        return False

def test_retrieval():
    """Test similarity search on ingested documents"""
    
    try:
        print("\n" + "="*50)
        print("Testing Retrieval")
        print("="*50)
        
        vector_store = VectorStore()
        
        test_queries = [
            "What is the refund policy?",
            "How do I cancel my subscription?",
            "What information do you collect?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            results = vector_store.similarity_search(query, k=2)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"\nResult {i}:")
                    print(f"Source: {result['metadata']['source']}, Page: {result['metadata']['page']}")
                    print(f"Text preview: {result['document'][:150]}...")
            else:
                print("No results found")
        
        return True
        
    except Exception as e:
        print(f"Error during retrieval test: {e}")
        return False

if __name__ == "__main__":
    print("Starting document ingestion pipeline...\n")
    
    Config.validate()
    
    success = ingest_sample_policies()
    
    if success:
        test_retrieval()
        print("\nStep 2 complete!")
    else:
        print("\nIngestion failed. Check error messages above.")
