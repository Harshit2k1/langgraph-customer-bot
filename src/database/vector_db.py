from sentence_transformers import SentenceTransformer
import lancedb
import numpy as np
import os
from src.config import Config

class VectorStore:
    """Manages document embeddings and similarity search using LanceDB"""
    
    def __init__(self):
        self.embedding_model = None
        self.db = None
        self.table = None
        self.dimension = 768
        self._initialize()
    
    def _initialize(self):
        """Initialize embedding model and LanceDB"""
        try:
            print(f"Loading embedding model: {Config.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
            
            os.makedirs(Config.VECTOR_STORE_PATH, exist_ok=True)
            
            self.db = lancedb.connect(Config.VECTOR_STORE_PATH)
            
            if "policy_documents" in self.db.table_names():
                self.table = self.db.open_table("policy_documents")
                print(f"LanceDB initialized at {Config.VECTOR_STORE_PATH}")
                print(f"Current collection size: {len(self.table)} documents")
            else:
                print("LanceDB initialized - no existing table")
                self.table = None
            
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            raise
    
    def embed_text(self, text):
        """Generate embeddings for given text"""
        if not text or not text.strip():
            return None
        
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def add_documents(self, documents, metadatas, ids):
        """Add documents to vector store with embeddings"""
        if not documents:
            print("No documents to add")
            return False
        
        try:
            valid_data = []
            
            for doc, metadata, doc_id in zip(documents, metadatas, ids):
                if doc and doc.strip():
                    embedding = self.embed_text(doc)
                    if embedding:
                        valid_data.append({
                            "id": doc_id,
                            "document": doc,
                            "source": metadata.get("source", "unknown"),
                            "page": metadata.get("page", 0),
                            "chunk_index": metadata.get("chunk_index", 0),
                            "vector": embedding
                        })
            
            if not valid_data:
                print("No valid documents to add after filtering")
                return False
            
            if self.table is None:
                self.table = self.db.create_table("policy_documents", data=valid_data)
            else:
                self.table.add(valid_data)
            
            print(f"Added {len(valid_data)} documents to vector store")
            return True
            
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def similarity_search(self, query, k=None):
        """Search for similar documents using query text"""
        if not query or not query.strip():
            return None
        
        if self.table is None:
            print("No documents in vector store")
            return None
        
        k = k or Config.TOP_K_RETRIEVAL
        
        try:
            query_embedding = self.embed_text(query)
            if not query_embedding:
                return None
            
            results = self.table.search(query_embedding).limit(k).to_list()
            
            if not results:
                return None
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'document': result['document'],
                    'metadata': {
                        'source': result['source'],
                        'page': result['page'],
                        'chunk_index': result['chunk_index']
                    },
                    'distance': result.get('_distance', 0),
                    'id': result['id']
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error during similarity search: {e}")
            return None
    
    def get_collection_stats(self):
        """Get statistics about the current collection"""
        try:
            if self.table is None:
                return {'total_documents': 0, 'collection_name': 'policy_documents'}
            
            count = len(self.table)
            return {
                'total_documents': count,
                'collection_name': 'policy_documents'
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {'total_documents': 0, 'collection_name': 'unknown'}
    
    def clear_collection(self):
        """Clear all documents from collection"""
        try:
            if self.table is not None:
                self.db.drop_table("policy_documents")
                self.table = None
            print("Collection cleared successfully")
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False
    
    def delete_by_source(self, source_filename):
        """Delete all chunks from a specific source file"""
        try:
            if self.table is None:
                return False
            
            all_data = self.table.to_pandas()
            
            filtered_data = all_data[all_data['source'] != source_filename]
            
            deleted_count = len(all_data) - len(filtered_data)
            
            if deleted_count == 0:
                return False
            
            self.db.drop_table("policy_documents")
            
            if len(filtered_data) > 0:
                data_list = filtered_data.to_dict('records')
                self.table = self.db.create_table("policy_documents", data=data_list)
            else:
                self.table = None
            
            print(f"Deleted {deleted_count} chunks from {source_filename}")
            return True
            
        except Exception as e:
            print(f"Error deleting by source: {e}")
            return False
    
    def get_all_sources(self):
        """Get list of all unique source files in collection"""
        try:
            if self.table is None:
                return []
            
            df = self.table.to_pandas()
            sources = df['source'].unique().tolist()
            
            return sorted(sources)
            
        except Exception as e:
            print(f"Error getting sources: {e}")
            return []
