"""
Test script for retriever module.

This script tests the retrieval functions to ensure they work correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from retriever import (
    retrieve_schema_info,
    retrieve_validation_rules,
    retrieve_combined,
    retrieve_by_table
)


def test_schema_retrieval():
    """Test retrieving schema information."""
    print("=" * 60)
    print("TEST 1: Schema Retrieval")
    print("=" * 60)
    
    query = "Tell me about the claims table"
    print(f"\n📝 Query: {query}\n")
    
    results = retrieve_schema_info(query, k=2)
    
    print(f"✅ Retrieved {len(results)} documents\n")
    for i, doc in enumerate(results, 1):
        print(f"--- Document {i} ---")
        print(f"Table: {doc['metadata'].get('table_name', 'N/A')}")
        print(f"Content preview: {doc['content'][:200]}...\n")


def test_rules_retrieval():
    """Test retrieving validation rules."""
    print("=" * 60)
    print("TEST 2: Validation Rules Retrieval")
    print("=" * 60)
    
    query = "What are the data quality rules for claims?"
    print(f"\n📝 Query: {query}\n")
    
    results = retrieve_validation_rules(query, k=3)
    
    print(f"✅ Retrieved {len(results)} documents\n")
    for i, doc in enumerate(results, 1):
        print(f"--- Document {i} ---")
        print(f"Rule ID: {doc['metadata'].get('rule_id', 'N/A')}")
        print(f"Rule Type: {doc['metadata'].get('rule_type', 'N/A')}")
        print(f"Severity: {doc['metadata'].get('severity', 'N/A')}")
        print(f"Content preview: {doc['content'][:150]}...\n")


def test_combined_retrieval():
    """Test retrieving from both collections."""
    print("=" * 60)
    print("TEST 3: Combined Retrieval")
    print("=" * 60)
    
    query = "Show me member information and related validation rules"
    print(f"\n📝 Query: {query}\n")
    
    results = retrieve_combined(query, schema_k=2, rules_k=2)
    
    print(f"✅ Retrieved {len(results['schema'])} schema docs, {len(results['rules'])} rule docs\n")
    
    print("Schema Documents:")
    for i, doc in enumerate(results['schema'], 1):
        print(f"  {i}. Table: {doc['metadata'].get('table_name', 'N/A')}")
    
    print("\nValidation Rule Documents:")
    for i, doc in enumerate(results['rules'], 1):
        print(f"  {i}. Rule: {doc['metadata'].get('rule_id', 'N/A')} - {doc['metadata'].get('severity', 'N/A')}")


def test_table_lookup():
    """Test retrieving specific table schema."""
    print("\n" + "=" * 60)
    print("TEST 4: Table Lookup")
    print("=" * 60)
    
    table_name = "providers"
    print(f"\n📝 Looking up table: {table_name}\n")
    
    result = retrieve_by_table(table_name)
    
    if result:
        print(f"✅ Found table: {result['metadata'].get('table_name', 'N/A')}")
        print(f"\nContent preview:\n{result['content'][:300]}...\n")
    else:
        print("❌ Table not found")


if __name__ == "__main__":
    print("\n🧪 TESTING RETRIEVER MODULE\n")
    
    try:
        test_schema_retrieval()
        print("\n")
        test_rules_retrieval()
        print("\n")
        test_combined_retrieval()
        print("\n")
        test_table_lookup()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        raise
