"""
Retrieval functions for querying vector stores.

This module provides functions to search schema and validation rules
based on user queries.
"""

from typing import List, Dict, Any
from retriever.vector_store import get_vector_stores


def retrieve_schema_info(query: str, k: int = 3) -> List[Dict[str, Any]]:
    """
    Retrieve relevant schema information based on a query.
    
    Args:
        query: The user's question about schema/tables
        k: Number of results to return (default: 3)
    
    Returns:
        List of documents with schema information
    """
    vector_stores = get_vector_stores()
    schema_store = vector_stores.get_schema_store()
    
    # Perform similarity search
    results = schema_store.similarity_search(query, k=k)
    
    # Convert to dictionary format
    documents = []
    for doc in results:
        documents.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "source": "schema"
        })
    
    return documents


def retrieve_validation_rules(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve relevant validation rules based on a query.
    
    Args:
        query: The user's question about validation rules
        k: Number of results to return (default: 5)
    
    Returns:
        List of documents with validation rules
    """
    vector_stores = get_vector_stores()
    rules_store = vector_stores.get_rules_store()
    
    # Perform similarity search
    results = rules_store.similarity_search(query, k=k)
    
    # Convert to dictionary format
    documents = []
    for doc in results:
        documents.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "source": "validation_rules"
        })
    
    return documents


def retrieve_combined(query: str, schema_k: int = 2, rules_k: int = 3) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieve from both schema and validation rules.
    
    Useful when the query might need both types of information.
    
    Args:
        query: The user's question
        schema_k: Number of schema results (default: 2)
        rules_k: Number of rules results (default: 3)
    
    Returns:
        Dictionary with 'schema' and 'rules' keys containing respective documents
    """
    schema_docs = retrieve_schema_info(query, k=schema_k)
    rules_docs = retrieve_validation_rules(query, k=rules_k)
    
    return {
        "schema": schema_docs,
        "rules": rules_docs
    }


def retrieve_by_table(table_name: str) -> Dict[str, Any]:
    """
    Retrieve schema info for a specific table.
    
    Args:
        table_name: Name of the table (e.g., "claims", "members")
    
    Returns:
        Schema document for the table, or None if not found
    """
    vector_stores = get_vector_stores()
    schema_store = vector_stores.get_schema_store()
    
    # Search with table name as query
    results = schema_store.similarity_search(f"Table: {table_name}", k=1)
    
    if results:
        return {
            "content": results[0].page_content,
            "metadata": results[0].metadata,
            "source": "schema"
        }
    return None


def retrieve_rules_by_type(rule_type: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve validation rules filtered by type.
    
    Args:
        rule_type: Type of rule ('Data Quality' or 'Business Rule')
        k: Number of results to return
    
    Returns:
        List of validation rule documents
    """
    vector_stores = get_vector_stores()
    rules_store = vector_stores.get_rules_store()
    
    # Search with rule type in query
    query = f"{rule_type} validation rules"
    results = rules_store.similarity_search(query, k=k)
    
    # Filter by actual rule type in metadata
    documents = []
    for doc in results:
        if doc.metadata.get("rule_type") == rule_type:
            documents.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "source": "validation_rules"
            })
    
    return documents
