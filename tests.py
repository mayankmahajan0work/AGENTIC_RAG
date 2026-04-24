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
from config.settings import validate_settings

# Track test results
test_results = {"passed": 0, "failed": 0, "errors": []}

def assert_test(condition: bool, message: str):
    """Simple assertion helper."""
    if condition:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        test_results["errors"].append(message)
        print(f"❌ ASSERTION FAILED: {message}")


# ============================================================================
# AGENT TESTS
# ============================================================================

def test_router():
    """Test intent classification."""
    print("=" * 80)
    print("TEST: Router Agent - Intent Classification")
    print("=" * 80)
    
    test_cases = [
        ("What columns are in the claims table?", "schema"),
        ("How do I check for duplicate claims?", "validation"),
        ("Generate SQL query to find all denied claims", "sql"),
        ("How are members and providers related?", "schema"),  # Merged into schema
    ]
    
    for query, expected_intent in test_cases:
        print(f"\n📝 Query: {query}")
        result = classify_intent_with_reasoning(query)
        print(f"🎯 Intent: {result['intent'].value}")
        print(f"💭 {result['reasoning']}")
        
        # Assertion: Check intent is correct
        assert_test(
            result['intent'].value == expected_intent,
            f"Expected intent '{expected_intent}' but got '{result['intent'].value}' for query: {query}"
        )


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
    
    # Assertions: Check response is not empty and mentions columns
    assert_test(len(response) > 0, "Response should not be empty")
    assert_test("claim_id" in response.lower() or "column" in response.lower(), 
                "Response should mention columns or specific column names")


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
    
    # Assertions: Check response includes SQL and mentions duplicates
    assert_test(len(response) > 0, "Response should not be empty")
    assert_test("SELECT" in response or "sql" in response.lower(), 
                "Validation response should include or reference SQL")
    assert_test("duplicate" in response.lower(), 
                "Response should mention duplicates")


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
    
    # Assertions: Check SQL is generated correctly
    assert_test(len(response) > 0, "SQL response should not be empty")
    assert_test("SELECT" in response, "SQL should contain SELECT")
    assert_test("claims" in response.lower(), "SQL should reference claims table")
    assert_test("billed_amount" in response.lower() or "10000" in response, 
                "SQL should filter by billed amount")


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
    
    # Assertions: Check retrieval works
    assert_test(len(results) > 0, "Should retrieve at least one document")
    assert_test(len(results) <= 2, "Should not exceed k=2 documents")


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
    
    # Assertions: Check retrieval works
    assert_test(len(results) > 0, "Should retrieve at least one rule document")
    assert_test(len(results) <= 3, "Should not exceed k=3 documents")


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
    test_complex_query()
    
    print("\n✅ Workflow tests completed!\n")


def run_all_tests():
    """Run complete test suite."""
    # Validate config first
    validate_settings()
    
    print("\n" + "="*80)
    print("🧪 RUNNING COMPLETE TEST SUITE")
    print("="*80)
    
    try:
        run_agent_tests()
        run_retriever_tests()
        run_workflow_tests()
        
        print("\n" + "="*80)
        if test_results["failed"] == 0:
            print("✅ ALL TESTS PASSED!")
        else:
            print(f"⚠️ SOME TESTS FAILED")
        print("="*80)
        print(f"""
📊 Test Summary:
  ✅ Passed: {test_results['passed']}
  ❌ Failed: {test_results['failed']}
  
🎯 Test Coverage:
  ✓ Agent tests: Router classification and response generation
  ✓ Retriever tests: Vector search from both indexes  
  ✓ Workflow tests: End-to-end RAG pipeline
  
The system is {'working correctly!' if test_results['failed'] == 0 else 'has issues - see errors above'}        """)
        
        if test_results["failed"] > 0:
            print("\n❌ Failed Assertions:")
            for error in test_results["errors"]:
                print(f"  - {error}")
            sys.exit(1)
        
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
