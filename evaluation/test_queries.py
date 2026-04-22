"""
Curated test queries for RAG system evaluation.

Each test query includes:
- question: The user's query
- expected_intent: What the router should classify it as
- expected_sources: Which tables/rules should be retrieved
- ground_truth: Expected answer or SQL pattern
- evaluation_criteria: What makes a good answer
"""

from typing import List, Dict, Any


TEST_QUERIES = [
    # ========================================================================
    # SCHEMA QUERIES - Understanding database structure
    # ========================================================================
    {
        "question": "What columns are in the claims table?",
        "expected_intent": "schema",
        "expected_sources": ["claims"],
        "ground_truth": "claims table has: claim_id, member_id, provider_id, product_id, service_date, submission_date, claim_status, billed_amount, allowed_amount, paid_amount, place_of_service, prior_auth_number",
        "evaluation_criteria": "Must list all 12 columns with data types"
    },
    {
        "question": "What is the primary key of the members table?",
        "expected_intent": "schema",
        "expected_sources": ["members"],
        "ground_truth": "member_id is the primary key",
        "evaluation_criteria": "Must identify member_id as primary key"
    },
    {
        "question": "What data type is billed_amount?",
        "expected_intent": "schema",
        "expected_sources": ["claims"],
        "ground_truth": "DECIMAL(10,2)",
        "evaluation_criteria": "Must specify correct data type"
    },
    
    # ========================================================================
    # VALIDATION QUERIES - Data quality rules
    # ========================================================================
    {
        "question": "How do I check for duplicate claims?",
        "expected_intent": "validation",
        "expected_sources": ["DQ_004"],
        "ground_truth": "Query to find claims with same member_id, provider_id, service_date, and billed_amount",
        "evaluation_criteria": "Must provide SQL that groups by these 4 columns and checks for COUNT > 1"
    },
    {
        "question": "How do I validate member eligibility on service date?",
        "expected_intent": "validation",
        "expected_sources": ["BR_001"],
        "ground_truth": "Check if service_date is between coverage_start_date and coverage_end_date",
        "evaluation_criteria": "Must check service_date against member coverage dates"
    },
    {
        "question": "What validation rules exist for claim amounts?",
        "expected_intent": "validation",
        "expected_sources": ["DQ_001", "DQ_009"],
        "ground_truth": "Billed amount must be positive, paid <= allowed <= billed",
        "evaluation_criteria": "Must mention amount hierarchy and positive constraint"
    },
    
    # ========================================================================
    # SQL GENERATION QUERIES - Generate working SQL
    # ========================================================================
    {
        "question": "Find all claims with billed_amount > 5000",
        "expected_intent": "sql",
        "expected_sources": ["claims"],
        "ground_truth": "SELECT * FROM claims WHERE billed_amount > 5000",
        "evaluation_criteria": "Must generate valid SQL with correct table and column"
    },
    {
        "question": "Write SQL to get claims with member names",
        "expected_intent": "sql",
        "expected_sources": ["claims", "members"],
        "ground_truth": "SELECT c.*, m.first_name, m.last_name FROM claims c JOIN members m ON c.member_id = m.member_id",
        "evaluation_criteria": "Must JOIN claims and members tables correctly"
    },
    {
        "question": "Show claims for diagnosis code D0.2",
        "expected_intent": "sql",
        "expected_sources": ["claim_lines"],
        "ground_truth": "SELECT * FROM claim_lines WHERE diagnosis_code = 'D0.2'",
        "evaluation_criteria": "Must query claim_lines table with correct column"
    },
    {
        "question": "Find members who are currently active",
        "expected_intent": "sql",
        "expected_sources": ["members"],
        "ground_truth": "SELECT * FROM members WHERE coverage_end_date IS NULL OR coverage_end_date > CURRENT_DATE",
        "evaluation_criteria": "Must check coverage_end_date appropriately"
    },
    {
        "question": "Get total billed amount per provider",
        "expected_intent": "sql",
        "expected_sources": ["claims", "providers"],
        "ground_truth": "SELECT p.provider_name, SUM(c.billed_amount) FROM claims c JOIN providers p ON c.provider_id = p.provider_id GROUP BY p.provider_name",
        "evaluation_criteria": "Must use SUM and GROUP BY with proper JOIN"
    },
    
    # ========================================================================
    # RELATIONSHIP QUERIES - Understanding table connections
    # ========================================================================
    {
        "question": "How are claims and members tables related?",
        "expected_intent": "relationship",
        "expected_sources": ["claims", "members"],
        "ground_truth": "claims.member_id → members.member_id",
        "evaluation_criteria": "Must identify the foreign key relationship"
    },
    {
        "question": "What tables link to the products table?",
        "expected_intent": "relationship",
        "expected_sources": ["products", "claims", "members"],
        "ground_truth": "members.product_id and claims.product_id both link to products.product_id",
        "evaluation_criteria": "Must identify both foreign key relationships"
    },
    {
        "question": "How do I join claim_lines to claims?",
        "expected_intent": "relationship",
        "expected_sources": ["claims", "claim_lines"],
        "ground_truth": "claim_lines.claim_id → claims.claim_id",
        "evaluation_criteria": "Must show the JOIN syntax with correct foreign key"
    },
    
    # ========================================================================
    # EDGE CASES - Testing system boundaries
    # ========================================================================
    {
        "question": "Find providers in Massachusetts",
        "expected_intent": "sql",
        "expected_sources": ["providers"],
        "ground_truth": "Cannot generate - providers table has no location/state column",
        "evaluation_criteria": "Must refuse and explain missing column"
    },
    {
        "question": "Show member credit card numbers",
        "expected_intent": "schema",
        "expected_sources": ["members"],
        "ground_truth": "members table does not contain credit card information",
        "evaluation_criteria": "Must correctly state the column doesn't exist"
    },
    
    # ========================================================================
    # COMPLEX QUERIES - Multi-step reasoning
    # ========================================================================
    {
        "question": "Find members who have claims over $10000",
        "expected_intent": "sql",
        "expected_sources": ["claims", "members"],
        "ground_truth": "SELECT m.* FROM members m JOIN claims c ON m.member_id = c.member_id WHERE c.billed_amount > 10000",
        "evaluation_criteria": "Must JOIN tables and filter by amount"
    },
    {
        "question": "Which claims were submitted after the service date by more than 90 days?",
        "expected_intent": "sql",
        "expected_sources": ["claims"],
        "ground_truth": "SELECT * FROM claims WHERE DATEDIFF(submission_date, service_date) > 90",
        "evaluation_criteria": "Must calculate date difference correctly"
    },
    {
        "question": "Show providers who have submitted claims with invalid procedure codes",
        "expected_intent": "sql",
        "expected_sources": ["claims", "claim_lines", "procedure_codes", "providers"],
        "ground_truth": "Must join multiple tables to find procedure codes not in reference table",
        "evaluation_criteria": "Must JOIN claim_lines, procedure_codes, claims, and providers with LEFT JOIN to find NULLs"
    }
]


def get_test_queries_by_type(intent_type: str) -> List[Dict[str, Any]]:
    """
    Filter test queries by intent type.
    
    Args:
        intent_type: One of 'schema', 'validation', 'sql', 'relationship'
    
    Returns:
        List of test queries matching the intent type
    """
    return [q for q in TEST_QUERIES if q['expected_intent'] == intent_type]


def get_test_query_count() -> Dict[str, int]:
    """
    Get count of test queries by type.
    
    Returns:
        Dictionary with counts per intent type
    """
    counts = {}
    for query in TEST_QUERIES:
        intent = query['expected_intent']
        counts[intent] = counts.get(intent, 0) + 1
    return counts


# Quick validation
if __name__ == "__main__":
    print("="*80)
    print("TEST QUERIES SUMMARY")
    print("="*80)
    
    counts = get_test_query_count()
    total = len(TEST_QUERIES)
    
    print(f"\nTotal test queries: {total}\n")
    for intent, count in sorted(counts.items()):
        print(f"  {intent:12s}: {count:2d} queries")
    
    print("\n" + "="*80)
    print("SAMPLE QUERIES BY TYPE")
    print("="*80)
    
    for intent in sorted(set(q['expected_intent'] for q in TEST_QUERIES)):
        samples = get_test_queries_by_type(intent)[:2]  # First 2 of each type
        print(f"\n{intent.upper()}:")
        for i, q in enumerate(samples, 1):
            print(f"  {i}. {q['question']}")
