"""
Load schema data into Chroma vector store.

This script reads claims_schema.json and creates embeddings for each table,
then stores them in the "schema_knowledge" collection.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import from config, models, etc.
# This lets us run this file directly: python ingestion/load_schema.py
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from config import settings


def load_schema_data():
    """
    Read the schema JSON file and convert it to text documents.
    
    Returns:
        List of Document objects, one for each table
    """
    print(f"📖 Reading schema file: {settings.SCHEMA_FILE}")
    
    with open(settings.SCHEMA_FILE, 'r') as f:
        schema_data = json.load(f)
    
    documents = []
    
    # Process each table
    for table in schema_data['tables']:
        # Create a text representation of the table
        content = f"""
Table: {table['table_name']}
Description: {table['description']}

Columns:
"""
        # Add each column
        for col in table['columns']:
            content += f"- {col['name']} ({col['data_type']}): {col['description']}\n"
        
        # Add relationships
        if table.get('relationships'):
            content += f"\nRelationships:\n"
            for rel in table['relationships']:
                content += f"- {rel}\n"
        
        # Add business context
        content += f"\nBusiness Context:\n{table.get('business_context', 'N/A')}"
        
        # Create a Document object with metadata
        doc = Document(
            page_content=content,
            metadata={
                "source": "schema",
                "table_name": table['table_name'],
                "type": "table_definition"
            }
        )
        documents.append(doc)
    
    print(f"✅ Loaded {len(documents)} tables from schema")
    return documents


def create_schema_index():
    """
    Create the schema vector store and load all documents.
    
    This creates embeddings and stores them in Chroma.
    """
    print("\n🚀 Starting schema ingestion...")
    
    # Check if collection exists and delete it to prevent duplicates
    try:
        client = chromadb.PersistentClient(path=str(settings.CHROMA_DB_DIR))
        try:
            client.delete_collection(name=settings.SCHEMA_COLLECTION)
            print(f"🗑️  Deleted existing collection: {settings.SCHEMA_COLLECTION}")
        except:
            pass  # Collection doesn't exist, that's fine
    except:
        pass  # No existing database, that's fine
    
    # Load documents
    documents = load_schema_data()
    
    # Create embeddings
    print(f"🔮 Creating embeddings using {settings.EMBEDDING_MODEL}...")
    embeddings = OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL
    )
    
    # Create vector store
    print(f"💾 Storing in Chroma at {settings.CHROMA_DB_DIR}...")
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=settings.SCHEMA_COLLECTION,
        persist_directory=str(settings.CHROMA_DB_DIR)
    )
    
    print(f"✅ Schema index created successfully!")
    print(f"   Collection: {settings.SCHEMA_COLLECTION}")
    print(f"   Documents: {len(documents)}")
    print(f"   Location: {settings.CHROMA_DB_DIR}")
    
    return vector_store


if __name__ == "__main__":
    # Run this script directly to create the schema index
    create_schema_index()
    print("\n🎉 Done! Schema data is ready for retrieval.")
