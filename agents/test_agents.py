"""
Test script for agents module.

Tests the router (intent classification) and response generator.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import classify_intent_with_reasoning, generate_response
from retriever import retrieve_schema_info, retrieve_validation_rules, retrieve_combined
from models.enums import IntentType


def test_router():
    """Test intent classification."""
    print("=" * 80)
    print("TEST 1: Router Agent - Intent Classification")
    print("=" * 80)
    
    test_queries = [
        "What columns are in the claims table?",
        "How do I check for duplicate claims?",
        "Write SQL to find all denied claims",
        "How are members and providers related?"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        result = classify_intent_with_reasoning(query)
        print(f"🎯 Intent: {result['intent'].value}")
        print(f"💭 {result['reasoning']}")


def test_schema_response():
    """Test response generation for schema questions."""
    print("\n\n" + "=" * 80)
    print("TEST 2: Response Generator - Schema Question")
    print("=" * 80)
    
    query = "What columns are in the claims table?"
    print(f"\n📝 Query: {query}\n")
    
    # Retrieve context
    schema_docs = retrieve_schema_info("claims table", k=1)
    
    # Generate response
    response = generate_response(
        query=query,
        intent=IntentType.SCHEMA,
        schema_docs=schema_docs
    )
    
    print("🤖 Response:")
    print("-" * 80)
    print(response)
    print("-" * 80)


def test_validation_response():
    """Test response generation for validation questions."""
    print("\n\n" + "=" * 80)
    print("TEST 3: Response Generator - Validation Question")
    print("=" * 80)
    
    query = "How do I check for duplicate claims?"
    print(f"\n📝 Query: {query}\n")
    
    # Retrieve context
    rules_docs = retrieve_validation_rules("duplicate claims", k=2)
    
    # Generate response
    response = generate_response(
        query=query,
        intent=IntentType.VALIDATION,
        rules_docs=rules_docs
    )
    
    print("🤖 Response:")
    print("-" * 80)
    print(response)
    print("-" * 80)


def test_sql_generation():
    """Test SQL query generation."""
    print("\n\n" + "=" * 80)
    print("TEST 4: Response Generator - SQL Generation")
    print("=" * 80)
    
    query = "Write SQL to find all claims with billed amount over $10,000"
    print(f"\n📝 Query: {query}\n")
    
    # Retrieve context
    combined = retrieve_combined("claims table billed amount", schema_k=2, rules_k=1)
    
    # Generate SQL
    response = generate_response(
        query=query,
        intent=IntentType.SQL_GENERATION,
        schema_docs=combined['schema'],
        rules_docs=combined['rules']
    )
    
    print("🤖 Generated SQL:")
    print("-" * 80)
    print(response)
    print("-" * 80)


def test_relationship_response():
    """Test response for relationship questions."""
    print("\n\n" + "=" * 80)
    print("TEST 5: Response Generator - Relationship Question")
    print("=" * 80)
    
    query = "How do I join claims with members?"
    print(f"\n📝 Query: {query}\n")
    
    # Retrieve schema for both tables
    schema_docs = retrieve_schema_info("claims members tables join", k=2)
    
    # Generate response
    response = generate_response(
        query=query,
        intent=IntentType.RELATIONSHIP,
        schema_docs=schema_docs
    )
    
    print("🤖 Response:")
    print("-" * 80)
    print(response)
    print("-" * 80)


if __name__ == "__main__":
    print("\n🧪 TESTING AGENTS MODULE\n")
    
    try:
        test_router()
        test_schema_response()
        test_validation_response()
        test_sql_generation()
        test_relationship_response()
        
        print("\n\n" + "=" * 80)
        print("✅ ALL AGENT TESTS COMPLETED!")
        print("=" * 80)
        print("""
The agents can now:
  ✓ Classify user intent (router)
  ✓ Answer schema questions
  ✓ Explain validation rules
  ✓ Generate SQL queries
  ✓ Explain table relationships
        """)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise
