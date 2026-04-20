"""
Vector store management for Chroma collections.

This module handles connections to the Chroma vector stores
for schema and validation rules.
"""

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from config import settings


class VectorStoreManager:
    """
    Manages connections to Chroma vector stores.
    
    This class provides access to both schema and validation rules collections.
    """
    
    def __init__(self):
        """Initialize embeddings and vector store connections."""
        # Create embeddings once and reuse
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL
        )
        
        # Connect to schema collection
        self.schema_store = Chroma(
            collection_name=settings.SCHEMA_COLLECTION,
            embedding_function=self.embeddings,
            persist_directory=str(settings.CHROMA_DB_DIR)
        )
        
        # Connect to validation rules collection
        self.rules_store = Chroma(
            collection_name=settings.RULES_COLLECTION,
            embedding_function=self.embeddings,
            persist_directory=str(settings.CHROMA_DB_DIR)
        )
    
    def get_schema_store(self):
        """Get the schema knowledge vector store."""
        return self.schema_store
    
    def get_rules_store(self):
        """Get the validation rules vector store."""
        return self.rules_store


# Create a global instance for reuse
_vector_store_manager = None


def get_vector_stores():
    """
    Get or create the VectorStoreManager singleton.
    
    Returns:
        VectorStoreManager: The vector store manager instance
    """
    global _vector_store_manager
    if _vector_store_manager is None:
        _vector_store_manager = VectorStoreManager()
    return _vector_store_manager
