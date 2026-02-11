from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os
from src.config import Config

class VectorStore:
    """Manages document embeddings and similarity search using FAISS"""
    
    def __init__(self):
        self.embedding_model = None
        self.index = None
        self.documents = []
        self.metadatas = []
        self.ids = []
        self.dimension = 768
        
        self.index_path = os.path.join(Config.VECTOR_STORE_PATH, "faiss.index")
        self.metadata_path = os.path.join(Config.VECTOR_STORE_PATH, "metadata.pkl")
        
        self._initialize()
    
    def _initialize(self):
        """Initialize embedding model and FAISS index"""
        try:
            print(f"Loading embedding model: {Config.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
            
            os.makedirs(Config.VECTOR_STORE_PATH, exist_ok=True)
            
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                self._load_index()
                print(f"Loaded existing index with {len(self.documents)} documents")
            else:
                self.index = faiss.IndexFlatL2(self.dimension)
                print("Created new FAISS index")
            
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            raise
    
    def _load_index(self):
        """Load existing FAISS index and metadata"""
        try:
            self.index = faiss.read_index(self.index_path)
            
            with open(self.metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadatas = data['metadatas']
                self.ids = data['ids']
            
        except Exception as e:
            print(f"Error loading index: {e}")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            self.metadatas = []
            self.ids = []
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            faiss.write_index(self.index, self.index_path)
            
            data = {
                'documents': self.documents,
                'metadatas': self.metadatas,
                'ids': self.ids
            }
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(data, f)
            
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def embed_text(self, text):
        """Generate embeddings for given text"""
        if not text or not text.strip():
            return None
        
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def add_documents(self, documents, metadatas, ids):
        """Add documents to vector store with embeddings"""
        if not documents:
            print("No documents to add")
            return False
        
        try:
            valid_docs = []
            valid_metadatas = []
            valid_ids = []
            embeddings = []
            
            for doc, metadata, doc_id in zip(documents, metadatas, ids):
                if doc and doc.strip():
                    embedding = self.embed_text(doc)
                    if embedding is not None:
                        valid_docs.append(doc)
                        valid_metadatas.append(metadata)
                        valid_ids.append(doc_id)
                        embeddings.append(embedding)
            
            if not valid_docs:
                print("No valid documents to add after filtering")
                return False
            
            embeddings_array = np.array(embeddings).astype('float32')
            self.index.add(embeddings_array)
            
            self.documents.extend(valid_docs)
            self.metadatas.extend(valid_metadatas)
            self.ids.extend(valid_ids)
            
            self._save_index()
            
            print(f"Added {len(valid_docs)} documents to vector store")
            return True
            
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def similarity_search(self, query, k=None):
        """Search for similar documents using query text"""
        if not query or not query.strip():
            return None
        
        if len(self.documents) == 0:
            print("No documents in vector store")
            return None
        
        k = k or Config.TOP_K_RETRIEVAL
        k = min(k, len(self.documents))
        
        try:
            query_embedding = self.embed_text(query)
            if query_embedding is None:
                return None
            
            query_embedding = np.array([query_embedding]).astype('float32')
            
            distances, indices = self.index.search(query_embedding, k)
            
            formatted_results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents):
                    formatted_results.append({
                        'document': self.documents[idx],
                        'metadata': self.metadatas[idx],
                        'distance': float(distances[0][i]),
                        'id': self.ids[idx]
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error during similarity search: {e}")
            return None
    
    def get_collection_stats(self):
        """Get statistics about the current collection"""
        try:
            return {
                'total_documents': len(self.documents),
                'collection_name': 'policy_documents'
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return None
    
    def clear_collection(self):
        """Clear all documents from collection"""
        try:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            self.metadatas = []
            self.ids = []
            self._save_index()
            print("Collection cleared successfully")
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False
