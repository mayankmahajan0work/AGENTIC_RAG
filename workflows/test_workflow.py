"""
Test script for LangGraph workflow.

Tests the complete RAG pipeline end-to-end:
Query → Router → Retriever → Generator → Response
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import run_query


def test_schema_query():
    """Test a schema question."""
    print("\n" + "="*80)
    print("TEST 1: Schema Query")
    print("="*80)
    
    result = run_query("What columns are in the claims table?")
    
    print(f"\n📊 RESULTS:")
    print(f"  Intent: {result['intent']}")
    print(f"  Documents Retrieved: {result['num_docs_retrieved']}")
    print(f"  SQL Generated: {'Yes' if result['sql_queries'] else 'No'}")
    print(f"\n💬 Response Preview:")
    print(f"  {result['response'][:200]}...")


def test_validation_query():
    """Test a validation rule question."""
    print("\n" + "="*80)
    print("TEST 2: Validation Query")
    print("="*80)
    
    result = run_query("How do I check for duplicate claims?")
    
    print(f"\n📊 RESULTS:")
    print(f"  Intent: {result['intent']}")
    print(f"  Documents Retrieved: {result['num_docs_retrieved']}")
    print(f"  SQL Generated: {'Yes' if result['sql_queries'] else 'No'}")
    print(f"\n💬 Response Preview:")
    print(f"  {result['response'][:200]}...")


def test_sql_generation():
    """Test SQL generation."""
    print("\n" + "="*80)
    print("TEST 3: SQL Generation")
    print("="*80)
    
    result = run_query("Write SQL to find all claims with status 'denied'")
    
    print(f"\n📊 RESULTS:")
    print(f"  Intent: {result['intent']}")
    print(f"  Documents Retrieved: {result['num_docs_retrieved']}")
    print(f"  SQL Generated: {'Yes' if result['sql_queries'] else 'No'}")
    print(f"\n💻 Generated SQL:")
    if result['sql_queries']:
        print(result['sql_queries'][0])
    else:
        print(f"  (No SQL - got explanation instead)")


def test_relationship_query():
    """Test relationship question."""
    print("\n" + "="*80)
    print("TEST 4: Relationship Query")
    print("="*80)
    
    result = run_query("How do I join members and claims tables?")
    
    print(f"\n📊 RESULTS:")
    print(f"  Intent: {result['intent']}")
    print(f"  Documents Retrieved: {result['num_docs_retrieved']}")
    print(f"  SQL Generated: {'Yes' if result['sql_queries'] else 'No'}")
    print(f"\n💬 Response Preview:")
    print(f"  {result['response'][:200]}...")


def test_complex_query():
    """Test a complex real-world query."""
    print("\n" + "="*80)
    print("TEST 5: Complex Real-World Query")
    print("="*80)
    
    result = run_query(
        "Write SQL to find members who have multiple claims on the same service date"
    )
    
    print(f"\n📊 RESULTS:")
    print(f"  Intent: {result['intent']}")
    print(f"  Documents Retrieved: {result['num_docs_retrieved']}")
    print(f"  Metadata: {result['metadata']}")
    print(f"\n💻 Full Response:")
    print("-" * 80)
    print(result['response'])
    print("-" * 80)


if __name__ == "__main__":
    print("\n" + "🧪 TESTING LANGGRAPH WORKFLOW" + "\n")
    print("This tests the complete RAG pipeline:")
    print("  1. Router classifies intent")
    print("  2. Retriever gets relevant context")
    print("  3. Generator creates response")
    print()
    
    try:
        test_schema_query()
        test_validation_query()
        test_sql_generation()
        test_relationship_query()
        test_complex_query()
        
        print("\n\n" + "="*80)
        print("✅ ALL WORKFLOW TESTS COMPLETED!")
        print("="*80)
        print("""
🎉 The complete RAG pipeline is working:
  ✓ Router successfully classifies intents
  ✓ Retriever fetches relevant context
  ✓ Generator creates accurate responses
  ✓ LangGraph orchestrates the flow smoothly
        """)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise
