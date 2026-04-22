"""
Graph Builder - Constructs the LangGraph StateGraph.

This file handles graph construction - wiring nodes together.
"""

from langgraph.graph import StateGraph, END

from models.state import GraphState
from workflows.nodes import (
    router_node,
    schema_retriever_node,
    rules_retriever_node,
    both_retrievers_node,
    generator_node,
    route_query
)


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow with conditional routing.
    
    Flow:
    1. START → router
    2. router → [conditional routing based on intent]
       - SCHEMA/RELATIONSHIP → schema_retriever
       - VALIDATION → rules_retriever
       - SQL_GENERATION → both_retrievers
    3. All retrievers → generator
    4. generator → END
    
    Returns:
        StateGraph ready to compile and run
    """
    # Create graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("schema_retriever", schema_retriever_node)
    workflow.add_node("rules_retriever", rules_retriever_node)
    workflow.add_node("both_retrievers", both_retrievers_node)
    workflow.add_node("generator", generator_node)
    
    # Define edges
    workflow.set_entry_point("router")  # Start here
    
    # Conditional routing from router to appropriate retriever(s)
    workflow.add_conditional_edges(
        "router",  # From router node
        route_query,  # Use this function to decide routing
        {
            "schema_retriever": "schema_retriever",
            "rules_retriever": "rules_retriever",
            "both_retrievers": "both_retrievers"
        }
    )
    
    # All retrievers go to generator
    workflow.add_edge("schema_retriever", "generator")
    workflow.add_edge("rules_retriever", "generator")
    workflow.add_edge("both_retrievers", "generator")
    
    # Generator goes to end
    workflow.add_edge("generator", END)
    
    return workflow
