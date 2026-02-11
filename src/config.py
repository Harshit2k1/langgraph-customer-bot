import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    
    DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/database/customer_support.db")
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./vectorstore/lance_db")
    
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    
    TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", 4))
    MEMORY_WINDOW = int(os.getenv("MEMORY_WINDOW", 5))
    
    EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
    
    @classmethod
    def validate(cls):
        """Validate critical configuration values"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        os.makedirs(os.path.dirname(cls.DATABASE_PATH), exist_ok=True)
        os.makedirs(cls.VECTOR_STORE_PATH, exist_ok=True)
        
        return True
