"""
Load validation rules into Chroma vector store.

This script reads validation_rules.json and creates embeddings for each rule,
then stores them in the "validation_rules" collection.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import from config, models, etc.
# This lets us run this file directly: python ingestion/load_rules.py
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from config import settings


def load_rules_data():
    """
    Read the validation rules JSON file and convert to text documents.
    
    Returns:
        List of Document objects, one for each validation rule
    """
    print(f"📖 Reading rules file: {settings.RULES_FILE}")
    
    with open(settings.RULES_FILE, 'r') as f:
        rules_data = json.load(f)
    
    documents = []
    
    # Process each validation rule
    for rule in rules_data['validation_rules']:
        # Create a text representation of the rule
        content = f"""
Rule ID: {rule['rule_id']}
Rule Name: {rule['rule_name']}
Type: {rule['rule_type']}
Severity: {rule['severity']}

Description:
{rule['description']}

Affected Tables: {', '.join(rule['affected_tables'])}

SQL Validation Query:
{rule['sql_validation']}

Business Context:
{rule['business_context']}

Expected Result: {rule['expected_result']}
Remediation: {rule['remediation']}
"""
        
        # Create Document with metadata
        doc = Document(
            page_content=content,
            metadata={
                "source": "validation_rules",
                "rule_id": rule['rule_id'],
                "rule_type": rule['rule_type'],
                "severity": rule['severity'],
                "tables": rule['affected_tables']
            }
        )
        documents.append(doc)
    
    print(f"✅ Loaded {len(documents)} validation rules")
    return documents


def create_rules_index():
    """
    Create the validation rules vector store and load all documents.
    
    This creates embeddings and stores them in Chroma.
    """
    print("\n🚀 Starting validation rules ingestion...")
    
    # Load documents
    documents = load_rules_data()
    
    # Create embeddings
    print(f"🔮 Creating embeddings using {settings.EMBEDDING_MODEL}...")
    embeddings = OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY
    )
    
    # Create vector store
    print(f"💾 Storing in Chroma at {settings.CHROMA_DB_DIR}...")
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=settings.RULES_COLLECTION,
        persist_directory=str(settings.CHROMA_DB_DIR)
    )
    
    print(f"✅ Validation rules index created successfully!")
    print(f"   Collection: {settings.RULES_COLLECTION}")
    print(f"   Documents: {len(documents)}")
    print(f"   Location: {settings.CHROMA_DB_DIR}")
    
    return vector_store


if __name__ == "__main__":
    # Run this script directly to create the rules index
    create_rules_index()
    print("\n🎉 Done! Validation rules are ready for retrieval.")
