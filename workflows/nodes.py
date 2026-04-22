"""
Workflow Nodes - Individual processing steps in the RAG pipeline.

Each node function processes the state and returns updated state.
"""

from typing import Literal, List

from models.state import GraphState
from models.enums import IntentType
from agents.router import classify_intent
from agents.response_generator import generate_response
from retriever import (
    retrieve_schema_info,
    retrieve_validation_rules,
    retrieve_combined
)


# ============================================================================
# Helper Functions
# ============================================================================

def extract_source_names(docs: List[dict]) -> List[str]:
    """
    Extract table names or rule IDs from retrieved documents.
    
    Args:
        docs: List of document dictionaries
    
    Returns:
        List of source names (table names or rule IDs)
    """
    sources = []
    for doc in docs:
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})
        
        # Try to extract table name from content
        lines = content.split('\n')
        for line in lines[:3]:  # Check first few lines
            if line.startswith('Table:'):
                table_name = line.replace('Table:', '').strip()
                sources.append(f"Table: {table_name}")
                break
            elif 'Rule ID:' in line:
                rule_id = line.split('Rule ID:')[1].strip().split()[0]
                sources.append(f"Rule: {rule_id}")
                break
        else:
            # Fallback to metadata if available
            if 'table_name' in metadata:
                sources.append(f"Table: {metadata['table_name']}")
            elif 'rule_id' in metadata:
                sources.append(f"Rule: {metadata['rule_id']}")
            elif 'source' in metadata:
                sources.append(metadata['source'])
    
    return sources


# ============================================================================
# NODE FUNCTIONS
# ============================================================================

def router_node(state: GraphState) -> GraphState:
    """
    Node 1: Classify user intent and prepare for routing.
    
    Takes the user's query and determines what type of question it is.
    The intent will control which vector store(s) to query next.
    """
    query = state["query"]
    
    # Classify intent
    intent = classify_intent(query)
    
    # Update state
    state["intent"] = intent.value  # Store as string for JSON serialization
    state["metadata"]["router_decision"] = intent.value
    
    print(f"🎯 Router: Classified as '{intent.value}'")
    print(f"   → Will route to: {_get_routing_description(intent.value)}")
    
    return state


def schema_retriever_node(state: GraphState) -> GraphState:
    """
    Node 2a: Query SCHEMA_KNOWLEDGE vector store.
    
    Retrieves table schemas, column information, and relationships.
    """
    query = state["query"]
    
    # Get schema information
    docs = retrieve_schema_info(query, k=3)
    state["retrieved_context"] = docs
    state["metadata"]["retrieval_type"] = "schema_only"
    state["metadata"]["vector_store"] = "schema_knowledge"
    
    # Extract and store source names
    sources = extract_source_names(docs)
    state["metadata"]["sources"] = sources
    
    # Print detailed retrieval info
    print(f"📚 Schema Retriever: Found {len(docs)} documents from schema_knowledge store")
    if sources:
        print(f"   📊 Sources: {', '.join(sources)}")
    
    return state


def rules_retriever_node(state: GraphState) -> GraphState:
    """
    Node 2b: Query VALIDATION_RULES vector store.
    
    Retrieves data quality rules and validation checks.
    """
    query = state["query"]
    
    # Get validation rules
    docs = retrieve_validation_rules(query, k=5)
    state["retrieved_context"] = docs
    state["metadata"]["retrieval_type"] = "rules_only"
    state["metadata"]["vector_store"] = "validation_rules"
    
    # Extract and store source names
    sources = extract_source_names(docs)
    state["metadata"]["sources"] = sources
    
    # Print detailed retrieval info
    print(f"📚 Rules Retriever: Found {len(docs)} documents from validation_rules store")
    if sources:
        print(f"   📋 Sources: {', '.join(sources)}")
    
    return state


def both_retrievers_node(state: GraphState) -> GraphState:
    """
    Node 2c: Query BOTH vector stores.
    
    For SQL generation, we need both schema info and validation rules.
    """
    query = state["query"]
    
    # Get from both stores
    combined = retrieve_combined(query, schema_k=3, rules_k=2)
    
    # Flatten into single list
    all_docs = combined['schema'] + combined['rules']
    state["retrieved_context"] = all_docs
    state["metadata"]["retrieval_type"] = "combined"
    state["metadata"]["vector_stores"] = ["schema_knowledge", "validation_rules"]
    state["metadata"]["schema_count"] = len(combined['schema'])
    state["metadata"]["rules_count"] = len(combined['rules'])
    
    # Extract sources from both types
    schema_sources = extract_source_names(combined['schema'])
    rules_sources = extract_source_names(combined['rules'])
    state["metadata"]["schema_sources"] = schema_sources
    state["metadata"]["rules_sources"] = rules_sources
    state["metadata"]["sources"] = schema_sources + rules_sources
    
    # Print detailed retrieval info
    print(f"📚 Both Retrievers: Found {len(combined['schema'])} schemas + {len(combined['rules'])} rules")
    if schema_sources:
        print(f"   📊 Schema Sources: {', '.join(schema_sources)}")
    if rules_sources:
        print(f"   📋 Rules Sources: {', '.join(rules_sources)}")
    
    return state


def generator_node(state: GraphState) -> GraphState:
    """
    Node 3: Generate final response using LLM.
    
    Takes the query, intent, and retrieved context to generate
    the final answer (could be explanation or SQL query).
    """
    query = state["query"]
    intent_str = state["intent"]
    retrieved_docs = state["retrieved_context"]
    
    # Convert string back to enum
    intent = IntentType(intent_str)
    
    # Separate schema and rules if we have both
    schema_docs = [doc for doc in retrieved_docs if doc['metadata'].get('source') == 'schema_knowledge']
    rules_docs = [doc for doc in retrieved_docs if doc['metadata'].get('source') == 'validation_rules']
    
    # If no separation happened, use all docs as schema (for schema/relationship queries)
    if not schema_docs and not rules_docs:
        schema_docs = retrieved_docs
    
    # Generate response
    response = generate_response(
        query=query,
        intent=intent,
        schema_docs=schema_docs if schema_docs else None,
        rules_docs=rules_docs if rules_docs else None
    )
    
    # Add source attribution to response
    sources = state["metadata"].get("sources", [])
    if sources:
        response += f"\n\n---\n📚 **Sources Used:**\n"
        for source in sources:
            response += f"- {source}\n"
    
    # Update state
    state["response"] = response
    state["metadata"]["response_generated"] = True
    
    # Extract SQL if present (simple heuristic: contains SELECT)
    if "SELECT" in response.upper():
        state["sql_queries"] = [response]
        print(f"✅ Generator: Created SQL query ({len(response)} chars)")
    else:
        state["sql_queries"] = []
        print(f"✅ Generator: Created explanation ({len(response)} chars)")
    
    return state


# ============================================================================
# ROUTING LOGIC
# ============================================================================

def route_query(state: GraphState) -> Literal["schema_retriever", "rules_retriever", "both_retrievers"]:
    """
    Conditional routing function - decides which vector store(s) to query.
    
    Routes based on intent:
    - SCHEMA/RELATIONSHIP → schema_knowledge store
    - VALIDATION → validation_rules store
    - SQL_GENERATION → both stores
    
    Returns:
        Name of the next node to execute
    """
    intent = state["intent"]
    
    if intent in ["schema", "relationship"]:
        return "schema_retriever"
    elif intent == "validation":
        return "rules_retriever"
    elif intent == "sql":
        return "both_retrievers"
    else:
        # Default to schema
        return "schema_retriever"


def _get_routing_description(intent: str) -> str:
    """Helper to describe routing decision."""
    routes = {
        "schema": "schema_knowledge vector store",
        "relationship": "schema_knowledge vector store",
        "validation": "validation_rules vector store",
        "sql": "both vector stores"
    }
    return routes.get(intent, "schema_knowledge vector store")
