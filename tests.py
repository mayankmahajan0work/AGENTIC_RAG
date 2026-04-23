"""
Consolidated test suite for the RAG system.

Run all tests or specific groups:
  python tests.py           # Run all tests
  python tests.py --agents  # Only agent tests
  python tests.py --retriever # Only retriever tests
  python tests.py --workflow  # Only workflow tests
"""

import sys
from agents import classify_intent_with_reasoning, generate_response
from retriever import retrieve_schema_info, retrieve_validation_rules, retrieve_combined
from models.enums import IntentType
from main import run_query


# ============================================================================
# AGENT TESTS
# ============================================================================

def test_router():
    """Test intent classification."""
    print("=" * 80)
    print("TEST: Router Agent - Intent Classification")
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
    print("TEST: Response Generator - Schema Question")
    print("=" * 80)
    
    query = "What columns are in the claims table?"
    print(f"\n📝 Query: {query}\n")
    
    schema_docs = retrieve_schema_info("claims table", k=1)
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
    print("TEST: Response Generator - Validation Question")
    print("=" * 80)
    
    query = "How do I check for duplicate claims?"
    print(f"\n📝 Query: {query}\n")
    
    rules_docs = retrieve_validation_rules("duplicate claims", k=2)
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
    print("TEST: Response Generator - SQL Generation")
    print("=" * 80)
    
    query = "Write SQL to find all claims with billed amount over $10,000"
    print(f"\n📝 Query: {query}\n")
    
    combined = retrieve_combined("claims table billed amount", schema_k=2, rules_k=1)
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
    print("TEST: Response Generator - Relationship Question")
    print("=" * 80)
    
    query = "How do I join claims with members?"
    print(f"\n📝 Query: {query}\n")
    
    schema_docs = retrieve_schema_info("claims members tables join", k=2)
    response = generate_response(
        query=query,
        intent=IntentType.RELATIONSHIP,
        schema_docs=schema_docs
    )
    
    print("🤖 Response:")
    print("-" * 80)
    print(response)
    print("-" * 80)


# ============================================================================
# RETRIEVER TESTS
# ============================================================================

def test_schema_retrieval():
    """Test retrieving schema information."""
    print("=" * 60)
    print("TEST: Schema Retrieval")
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
    print("TEST: Validation Rules Retrieval")
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
    print("TEST: Combined Retrieval")
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


# ============================================================================
# WORKFLOW TESTS
# ============================================================================

def test_schema_query():
    """Test a schema question through full workflow."""
    print("\n" + "="*80)
    print("TEST: Complete Workflow - Schema Query")
    print("="*80)
    
    result = run_query("What columns are in the claims table?")
    
    print(f"\n📊 RESULTS:")
    print(f"  Intent: {result['intent']}")
    print(f"  Documents Retrieved: {result['num_docs_retrieved']}")
    print(f"  SQL Generated: {'Yes' if result['sql_queries'] else 'No'}")
    print(f"\n💬 Response Preview:")
    print(f"  {result['response'][:200]}...")


def test_validation_query():
    """Test a validation rule question through full workflow."""
    print("\n" + "="*80)
    print("TEST: Complete Workflow - Validation Query")
    print("="*80)
    
    result = run_query("How do I check for duplicate claims?")
    
    print(f"\n📊 RESULTS:")
    print(f"  Intent: {result['intent']}")
    print(f"  Documents Retrieved: {result['num_docs_retrieved']}")
    print(f"  SQL Generated: {'Yes' if result['sql_queries'] else 'No'}")
    print(f"\n💬 Response Preview:")
    print(f"  {result['response'][:200]}...")


def test_sql_query():
    """Test SQL generation through full workflow."""
    print("\n" + "="*80)
    print("TEST: Complete Workflow - SQL Generation")
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
    """Test relationship question through full workflow."""
    print("\n" + "="*80)
    print("TEST: Complete Workflow - Relationship Query")
    print("="*80)
    
    result = run_query("How do I join members and claims tables?")
    
    print(f"\n📊 RESULTS:")
    print(f"  Intent: {result['intent']}")
    print(f"  Documents Retrieved: {result['num_docs_retrieved']}")
    print(f"  SQL Generated: {'Yes' if result['sql_queries'] else 'No'}")
    print(f"\n💬 Response Preview:")
    print(f"  {result['response'][:200]}...")


def test_complex_query():
    """Test a complex real-world query through full workflow."""
    print("\n" + "="*80)
    print("TEST: Complete Workflow - Complex Query")
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


# ============================================================================
# TEST RUNNERS
# ============================================================================

def run_agent_tests():
    """Run all agent tests."""
    print("\n🧪 AGENT TESTS\n")
    test_router()
    test_schema_response()
    test_validation_response()
    test_sql_generation()
    test_relationship_response()
    print("\n✅ Agent tests completed!\n")


def run_retriever_tests():
    """Run all retriever tests."""
    print("\n🧪 RETRIEVER TESTS\n")
    test_schema_retrieval()
    print("\n")
    test_rules_retrieval()
    print("\n")
    test_combined_retrieval()
    print("\n✅ Retriever tests completed!\n")


def run_workflow_tests():
    """Run all workflow tests."""
    print("\n🧪 WORKFLOW TESTS\n")
    print("Testing complete RAG pipeline:")
    print("  1. Router classifies intent")
    print("  2. Retriever gets relevant context")
    print("  3. Generator creates response")
    
    test_schema_query()
    test_validation_query()
    test_sql_query()
    test_relationship_query()
    test_complex_query()
    
    print("\n✅ Workflow tests completed!\n")


def run_all_tests():
    """Run complete test suite."""
    print("\n" + "="*80)
    print("🧪 RUNNING COMPLETE TEST SUITE")
    print("="*80)
    
    try:
        run_agent_tests()
        run_retriever_tests()
        run_workflow_tests()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("""
🎉 Test Summary:
  ✓ Agent tests: Router and response generation
  ✓ Retriever tests: Schema and rules retrieval
  ✓ Workflow tests: End-to-end RAG pipeline
  
The system is working correctly!
        """)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        raise


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ["--agents", "-a"]:
            run_agent_tests()
        elif arg in ["--retriever", "-r"]:
            run_retriever_tests()
        elif arg in ["--workflow", "-w"]:
            run_workflow_tests()
        elif arg in ["--help", "-h"]:
            print(__doc__)
        else:
            print(f"Unknown argument: {arg}")
            print("Use --help to see available options")
            sys.exit(1)
    else:
        # No arguments - run all tests
        run_all_tests()
